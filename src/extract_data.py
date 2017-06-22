import os
import numpy as np
from p_tools import time_string
from core import airport_altitude, guess_alt_ths
from aircraft_model import Aircraft
from geo_resources import *


class Metrics:

    def __init__(self, dataExtractor):
        self.generic_current_diff = 0.0
        self.dataExtractor = dataExtractor
        self.epoch_now = 0

        # self.op32R = '32R'
        # self.op32L = '32L'
        # self.op36R = '36R'
        # self.op36L = '36L'
        # self.op14R = '14R'
        # self.op14L = '14L'
        # self.op18R = '18R'
        # self.op18L = '18L'

    def run(self, infile, icao_filter):
        filepath = infile.name
        master_name = os.path.splitext(os.path.basename(filepath))[0]

        try:
            database = open(filepath, 'r')
        except Exception:
            raise NameError('No valid input path')

        print_time = True
        prev_epoch = 0
        for i, master_line in enumerate(database):
            if i == 0:  # skip header
                continue
            data = master_line.split('\t')
            self.epoch_now = float(data[0])
            icao0 = str(data[2])

            if self.epoch_now < prev_epoch:
                # database going backwards, could be that raw data was already corrupt
                continue
            prev_epoch = self.epoch_now

            if self.epoch_now % 3600 == 0:
                if print_time:
                    print time_string(self.epoch_now) + ' ...'
                    print_time = False
            else:
                print_time = True

            if icao_filter is not None and icao0 != icao_filter:
                continue

            if icao0 not in self.dataExtractor.icao_dict.keys():
                self.dataExtractor.icao_dict[icao0] = Aircraft(icao0, self.epoch_now)
            current_aircraft = self.dataExtractor.icao_dict[icao0]
            current_aircraft.last_seen = self.epoch_now

            call = str(data[3]).strip()
            if call:  # call found in or outside airport.
                if call+icao0 not in self.dataExtractor.call_icao_list:  # record call+icao0 if seen more than once
                    self.dataExtractor.call_icao_list.append(call+icao0)
                else:
                    current_aircraft.set_call(call, self.epoch_now)  # already fixes unknown call to op_timestamp
            current_flight = current_aircraft.get_current_flight(self.epoch_now)  # will be no_call flight if new

            if str(data[8]) and str(data[9]) and str(data[10]):
                current_aircraft.set_new_vel(self.epoch_now, float(data[8]), float(data[9]), float(data[10]))

            if data[16]:  # kollsman found
                current_aircraft.set_kolls(float(data[16]))

            pos = None
            if data[4] and data[5]:  # latitude information
                lat = float(data[4])
                lon = float(data[5])
                FL = None
                alt_uncorrected = None
                if data[6]:
                    FL = float(data[6])
                    alt_uncorrected = FL * 30.48  # m, no QNH correction
                elif data[7]:  # should be "1"
                    # TODO include ground positions in analysis. If QNH not properly applied, a higher surface pos will make it think it was a missed apprach
                    # continue
                    alt_uncorrected = airport_altitude  # ground position. Will be corrected but doesn't really matter
                    FL = 20
                if FL is not None and FL < 130:  # FL130
                    pos = Point(lat, lon)

            if pos is not None and TMA.contains(pos):  # TODO here filter for cointainment in SID/STAR

                NorS = None
                EorW = None
                ttrack = None
                gs = None
                inclin = None
                poly = None
                vrate = None
                found_data = False

                current_aircraft.set_new_pos(self.epoch_now, lat, lon, alt_uncorrected)
                # prev20_5_pos = current_aircraft.get_position_delimited(self.epoch_now, 5, 20)
                prev_vel = current_aircraft.get_velocity_delimited(self.epoch_now, 0, 20)
                if prev_vel is not None:
                    vrate = prev_vel.vrate  # fpm
                    gs = prev_vel.gs  # knots
                    if gs == 0:
                        continue
                    ttrack = prev_vel.ttrack  # [0 , 360]
                    ttrack = ttrack % 360
                    inclin = np.rad2deg(np.arctan(vrate / gs * 0.0098748))
                    found_data = True

                # if prev20_5_pos is not None:
                #     diff = epoch_now - prev20_5_pos.epoch
                #     if 5.0 <= diff <= 20:  # min-max difference to obtain values
                #         vrate_intpl = (alt_uncorrected - prev20_5_pos.alt) / diff  # [m/s]
                #         vec = [lat - prev20_5_pos.lat, lon - prev20_5_pos.lon]
                #         hspeed = great_circle((lat, lon), (prev20_5_pos.lat, prev20_5_pos.lon)).meters / diff  # [m/s]
                #         track = math.atan2(-vec[1], vec[0])  # -pi to +pi
                #         inclin = np.rad2deg(np.arctan(vrate_intpl / hspeed))
                #         if track < 0:
                #             track += 2 * np.pi
                #         track = np.rad2deg(2 * np.pi - track) % 360
                #         # self.holding.set_track(call, icao0, track, epoch_now)  # INCOMPLETE CLASS!
                #         if vrate_intpl > 0:
                #             UorD = 'U'
                #         else:
                #             UorD = 'D'
                #         found_data = True

                if airport_poly.contains(pos) and found_data:

                    # | A1 - | B1
                    # | A0 - | B0
                    #    #####
                    #  \ C0 - \ D0
                    #   \ C1 - \ D1

                    if poly_SE.contains(pos):  # only for approaches
                        current_flight.set_guess(self.epoch_now, 'S', 'E', ttrack, vrate, inclin, gs, 4)
                    elif poly_SW.contains(pos):
                        current_flight.set_guess(self.epoch_now, 'S', 'W', ttrack, vrate, inclin, gs, 4)
                    elif poly_NE.contains(pos):
                        current_flight.set_guess(self.epoch_now, 'N', 'E', ttrack, vrate, inclin, gs, 4)
                    elif poly_NW.contains(pos):
                        current_flight.set_guess(self.epoch_now, 'N', 'W', ttrack, vrate, inclin, gs, 4)

                    if alt_uncorrected <= guess_alt_ths + airport_altitude:
                        current_diff = current_aircraft.get_current_diff()
                        if current_diff is not None:
                            self.generic_current_diff = current_diff
                        else:  # TODO make timer for 30 min to make new generic_current_diff
                            current_diff = self.generic_current_diff
                        alt_corr = alt_uncorrected - current_diff

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

                        if poly is not None:
                            # here we set the alt_ths_operation timestamp
                            prev30_10_pos = current_aircraft.get_position_delimited(self.epoch_now, 10, 30)
                            if prev30_10_pos is not None:  # can happen there was no prev data
                                prev_alt_corr = prev30_10_pos.alt - current_diff
                                prev_epoch = prev30_10_pos.epoch
                                # current_flight.operation.set_alt_ths_timestamp(epoch_now, prev_epoch, alt_corr, prev_alt_corr, NorS)

                            zone = int(poly[1])
                            current_flight.set_guess(self.epoch_now, NorS, EorW, ttrack, vrate, inclin, gs, zone)