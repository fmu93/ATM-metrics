import numpy as np
from p_tools import datetime_string
from aircraft_model import Aircraft
from geo_resources import *
from shapely.geometry import LineString
import time
import threading

time_between_waypoint = 60  # s
guess_alt_ths = 1800  # [m] ~5900 [ft] above airport to discard flyovers
airport_altitude = 600  # [m] ~ 1970 [ft]


class Metrics:

    def __init__(self, dataExtractor):
        self.dataExtractor = dataExtractor
        self.epoch_now = 0
        self.evaluate_waypoints = self.dataExtractor.core.evaluate_waypoints
        self.dead = False
        self.line_count = 0
        self.is_delimited = self.dataExtractor.core.is_delimited
        self.analyseStart = self.dataExtractor.core.analyseStart
        self.analyseEnd = self.dataExtractor.core.analyseEnd
        self.lock1 = threading.Lock()

    def run(self, key_timestamp, infile, icao_filter):
        # Open database
        filepath = infile.name
        try:
            database = open(filepath, 'r')
        except Exception:
            raise NameError('No valid input path')

        print_time = True
        prev_epoch = 0
        for i, current_line in enumerate(database):
            self.line_count += 1

            if i == 0:  # skip header
                continue
            if self.dead:
                break
            # wait while paused (triggered in GUI)
            while self.dataExtractor.paused:
                time.sleep(0.1)

            data = current_line.split('\t')
            self.epoch_now = float(data[0])
            icao0 = str(data[2])

            # filter time start and end
            if self.is_delimited:
                if self.analyseStart and self.epoch_now <= self.analyseStart:
                    continue
                if self.analyseEnd and self.epoch_now > self.analyseEnd:
                    break

            if self.epoch_now < prev_epoch:
                # database going backwards, could be that raw data was already corrupt
                continue
            prev_epoch = self.epoch_now

            # print hour to console and update clock and progress bar in GUI
            if self.epoch_now % 3600 == 0:
                if print_time:
                    print datetime_string(self.epoch_now) + ' ...'
                    print_time = False
                    self.dataExtractor.dispTime(datetime_string(self.epoch_now))
                    # progress bar TODO should be queued for main thread to process or might hang
                    self.dataExtractor.core.controller.update_progressbar(100 * self.line_count /
                                                                          self.dataExtractor.num_lines)
            else:
                print_time = True

            # icao filter. For now only editable in core
            if icao_filter is not None and icao0 != icao_filter:
                continue

            # get the icao_dict where aircraft model is and get the current aircraft
            with self.lock1:
                icao_dict = self.dataExtractor.core.files_data_dict[key_timestamp]
            if icao0 not in icao_dict.keys():
                icao_dict[icao0] = Aircraft(icao0, self.epoch_now)
            current_aircraft = icao_dict[icao0]
            current_aircraft.last_seen = self.epoch_now

            # check if current line has call information
            call = str(data[3]).strip()
            if call:  # call found in or outside airport.
                # record call+icao0 if seen more than once to avoid corrupt callsigns ()
                if call+icao0 not in self.dataExtractor.call_icao_list:
                    self.dataExtractor.call_icao_list.append(call+icao0)
                else:
                    current_aircraft.set_call(call, self.epoch_now)  # already fixes unknown call to op_timestamp

            # check if current line has velocity information and save it to the aircraft velocity buffer
            # TODO this is not efficient since we store for all ac in or out of TMA. Better only for those known to be within TMA
            if str(data[8]) and str(data[9]) and str(data[10]):
                # vrate, gs, ttrack
                current_aircraft.set_new_vel(self.epoch_now, float(data[8]), float(data[9]), float(data[10]))

            # check if current line has kollsman value
            if data[16]:  # kollsman found
                current_aircraft.set_kolls(float(data[16]), self.epoch_now)

            # check if current line has position and altitude information
            pos = None
            FL = None
            alt_uncorrected = None
            if data[4] and data[5] and (data[6] or data[7]):
                # VERY IMPORTANT! (lon, lat) as in (x, y) coordinates, everywhere in the program
                pos = Point(float(data[5]), float(data[4]))
                if data[6]:
                    FL = float(data[6])
                    alt_uncorrected = FL * 30.48  # m, no QNH correction
                elif data[7]:  # ground boolean
                    alt_uncorrected = airport_altitude  # ground position. Will be corrected but doesn't really matter
                    FL = 20
                # only store previous points if we are interested in waypoints
                if self.evaluate_waypoints:
                    current_aircraft.set_new_pos(self.epoch_now, pos.x, pos.y, alt_uncorrected)
            # get a new line if no position information (we already checked for any other kind of valuable info)
            else:
                continue

            # detect waypoints. Efficient manner by making lines between periodical points
            # TODO make more efficient by categorizing waypoints sections
            if self.evaluate_waypoints:
                current_flight = current_aircraft.get_current_flight()  # will be no_call flight if new
                line = None
                if self.epoch_now - current_aircraft.last_waypoint_check >= time_between_waypoint:
                    # make line between current position and time_between_waypoint position, or up to 10 minutes
                    prev_tbw_pos = current_aircraft.get_position_delimited(self.epoch_now, time_between_waypoint, 360)
                    if prev_tbw_pos:
                        line = LineString([pos, (prev_tbw_pos.lon, prev_tbw_pos.lat)])
                if line:
                    for waypoint in waypoints_dict.keys():
                        if line.crosses(waypoints_dict[waypoint]):
                            current_flight.set_waypoint(waypoint)
                    current_aircraft.last_waypoint_check = self.epoch_now

            # evaluate further only if below FL 130 and within TMA
            if pos and FL and alt_uncorrected and FL < 130 and airport_poly.contains(pos):
                # store prev positions only inside TMA if not interested in waypoints
                if not self.evaluate_waypoints:
                    current_flight = current_aircraft.get_current_flight()  # will be no_call flight if new
                    current_aircraft.set_new_pos(self.epoch_now, pos.x, pos.y, alt_uncorrected)

                NorS = None
                EorW = None
                poly = None

                prev_vel = current_aircraft.get_velocity_delimited(self.epoch_now, 0, 20)
                if prev_vel:
                    vrate = prev_vel.vrate  # fpm
                    gs = prev_vel.gs  # knots
                    if gs == 0:
                        continue  # TODO: what?
                    ttrack = prev_vel.ttrack  # [0 , 360]
                    ttrack = ttrack % 360
                    inclin = np.rad2deg(np.arctan(vrate / gs * 0.0098748))

                    # | A1 - | B1
                    # | A0 - | B0
                    #    #####
                    #  \ C0 - \ D0
                    #   \ C1 - \ D1

                    if poly_SE.contains(pos):  # ZONE 4, will only be useful for approaches
                        current_flight.set_guess(self.epoch_now, 'S', 'E', ttrack, vrate, inclin, gs, 4)
                    elif poly_SW.contains(pos):
                        current_flight.set_guess(self.epoch_now, 'S', 'W', ttrack, vrate, inclin, gs, 4)
                    elif poly_NE.contains(pos):
                        current_flight.set_guess(self.epoch_now, 'N', 'E', ttrack, vrate, inclin, gs, 4)
                    elif poly_NW.contains(pos):
                        current_flight.set_guess(self.epoch_now, 'N', 'W', ttrack, vrate, inclin, gs, 4)

                    if alt_uncorrected <= guess_alt_ths + airport_altitude:
                        if poly_north.contains(pos):
                            NorS = 'N'
                            if poly_AA.contains(pos):
                                EorW = 'W'
                                if poly_A0.contains(pos):
                                    poly = 'A0'
                                elif poly_A1.contains(pos):
                                    poly = 'A1'
                                elif poly_A2.contains(pos):
                                    poly = 'A2'
                                elif poly_A3.contains(pos):
                                    poly = 'A3'
                            elif poly_BB.contains(pos):
                                EorW = 'E'
                                if poly_B0.contains(pos):
                                    poly = 'B0'
                                elif poly_B1.contains(pos):
                                    poly = 'B1'
                                elif poly_B2.contains(pos):
                                    poly = 'B2'
                                elif poly_B3.contains(pos):
                                    poly = 'B3'
                        elif poly_south.contains(pos):
                            NorS = 'S'
                            if poly_CC.contains(pos):
                                EorW = 'W'
                                if poly_C0.contains(pos):
                                    poly = 'C0'
                                elif poly_C1.contains(pos):
                                    poly = 'C1'
                                elif poly_C2.contains(pos):
                                    poly = 'C2'
                                elif poly_C3.contains(pos):
                                    poly = 'C3'
                            elif poly_DD.contains(pos):
                                EorW = 'E'
                                if poly_D0.contains(pos):
                                    poly = 'D0'
                                elif poly_D1.contains(pos):
                                    poly = 'D1'
                                elif poly_D2.contains(pos):
                                    poly = 'D2'
                                elif poly_D3.contains(pos):
                                    poly = 'D3'

                        if poly:
                            zone = int(poly[1])
                            current_flight.set_guess(self.epoch_now, NorS, EorW, ttrack, vrate, inclin, gs, zone)

                            # here we set the alt_ths_operation timestamp
                            current_diff = current_aircraft.get_current_diff(self.epoch_now)
                            alt_corr = alt_uncorrected - current_diff

                            prev10_30_pos = current_aircraft.get_position_delimited(self.epoch_now, 10, 30)
                            if prev10_30_pos:  # can happen there was no prev data
                                prev_alt_corr = prev10_30_pos.alt - current_diff
                                prev_epoch = prev10_30_pos.epoch
                                if current_flight.operations:
                                    current_flight.operations[-1].set_alt_ths_timestamp(
                                        self.epoch_now, prev_epoch, alt_corr, prev_alt_corr, NorS)

        database.close()

    def stop(self):
        self.dead = True
        return True
