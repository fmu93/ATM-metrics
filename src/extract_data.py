import os
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
from p_tools import time_string
from core import airport_altitude, guess_alt_ths, icao_dict, call_icao_list
from aircraft_model import Aircraft


class Metrics:

    def __init__(self):
        self.generic_current_diff = 0.0

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

        if True:
            airport_poly = Polygon(((41.07961, -3.29377), (41.08127, -3.88696), (40.05861, -3.59719), (40.06891, -2.93164),
                                    (41.07961, -3.29377)))
            TMA = Polygon(((41.3, -4.1215), (41.103, -4.364), (39.562, -4.364), (39.331, -4.0805), (39.3525, -2.5505),
                           (39.5321, -2.2748), (40.0, -2.22), (40.0, -2.174), (40.052, -2.093), (41.0204, -2.093),
                           (41.02, -2.3), (41.18, -2.3), (41.3006, -2.2208), (41.3, -4.121)))
            poly_north = Polygon(((40.74744, -3.46352), (40.74478, -3.68924), (40.48915, -3.59233), (40.5006, -3.53872),
                                  (40.74744, -3.46352)))
            poly_south = Polygon(
                ((40.5028, -3.54558), (40.4771, -3.59287), (40.24947, -3.45302), (40.34823, -3.27294), (40.5028, -3.54558)))
            poly_AA = Polygon(((40.74416, -3.57195), (40.7419, -3.68776), (40.48824, -3.59247), (40.49252, -3.56693),
                               (40.74416, -3.57195)))
            poly_BB = Polygon(((40.49786, -3.56681), (40.50062, -3.53893), (40.74682, -3.46393), (40.74583, -3.57212),
                               (40.49786, -3.56681)))
            poly_CC = Polygon(
                ((40.49067, -3.56738), (40.47706, -3.59278), (40.25049, -3.4521), (40.2963, -3.3718), (40.49067, -3.56738)))
            poly_DD = Polygon(((40.29576, -3.37161), (40.34928, -3.27507), (40.50271, -3.54598), (40.49084, -3.56721),
                               (40.29576, -3.37161)))

            poly_A0 = Polygon(((40.49282, -3.57818), (40.49269, -3.57089), (40.52304, -3.57078), (40.52295, -3.58158),
                               (40.49282, -3.57818)))
            poly_A1 = Polygon(((40.57307, -3.56887), (40.57241, -3.61041), (40.52293, -3.59407), (40.52289, -3.56849),
                               (40.57307, -3.56887)))
            poly_A2 = Polygon(((40.63903, -3.56989), (40.63983, -3.64513), (40.57223, -3.62534), (40.57306, -3.56882),
                               (40.63903, -3.56989)))
            poly_A3 = Polygon(((40.74122, -3.57175), (40.74063, -3.63113), (40.63949, -3.60896), (40.63901, -3.56951),
                               (40.74122, -3.57175)))
            poly_B0 = Polygon(((40.4996, -3.56196), (40.49974, -3.55525), (40.52805, -3.55285), (40.52817, -3.56435),
                               (40.4996, -3.56196)))
            poly_B1 = Polygon(((40.52783, -3.53485), (40.5774, -3.52343), (40.57827, -3.56799), (40.5283, -3.56606),
                               (40.52783, -3.53485)))
            poly_B2 = Polygon(((40.57833, -3.56811), (40.57732, -3.51316), (40.64347, -3.5006), (40.64485, -3.56969),
                               (40.57833, -3.56811)))
            poly_B3 = Polygon(((40.64421, -3.53502), (40.74518, -3.51929), (40.74469, -3.57187), (40.64492, -3.56944),
                               (40.64421, -3.53502)))
            poly_C0 = Polygon(((40.48627, -3.57295), (40.48399, -3.57759), (40.46076, -3.55813), (40.46579, -3.54916),
                               (40.48627, -3.57295)))
            poly_C1 = Polygon(
                ((40.45225, -3.5738), (40.40969, -3.54418), (40.4293, -3.50577), (40.46681, -3.54683), (40.45225, -3.5738)))
            poly_C2 = Polygon(((40.40605, -3.55106), (40.34691, -3.50421), (40.37566, -3.45115), (40.42929, -3.50583),
                               (40.40605, -3.55106)))
            poly_C3 = Polygon(((40.37576, -3.45083), (40.35825, -3.48302), (40.27202, -3.41353), (40.29623, -3.37177),
                               (40.37576, -3.45083)))
            poly_D0 = Polygon(((40.49705, -3.55601), (40.49324, -3.56269), (40.47032, -3.54164), (40.47636, -3.5314),
                               (40.49705, -3.55601)))
            poly_D1 = Polygon(((40.45083, -3.46477), (40.48431, -3.51756), (40.46881, -3.54432), (40.42969, -3.50496),
                               (40.45083, -3.46477)))
            poly_D2 = Polygon(((40.37616, -3.45094), (40.41225, -3.38885), (40.45496, -3.45691), (40.42972, -3.50499),
                               (40.37616, -3.45094)))
            poly_D3 = Polygon(((40.29629, -3.37148), (40.32432, -3.32268), (40.39417, -3.41999), (40.3762, -3.45119),
                               (40.29629, -3.37148)))

            poly_NW = Polygon(((41.02731, -3.59283), (41.0809, -3.88569), (40.58557, -3.72914), (40.58742, -3.58284),
                               (41.02731, -3.59283)))
            poly_NE = Polygon(((40.58884, -3.55356), (40.59099, -3.37778), (41.0787, -3.29399), (41.02823, -3.55276),
                               (40.58884, -3.55356)))
            poly_SW = Polygon(((40.32802, -3.66551), (40.06082, -3.59183), (40.06778, -3.20344), (40.39949, -3.52975),
                               (40.32802, -3.66551)))
            poly_SE = Polygon(((40.43686, -3.46864), (40.07006, -3.07089), (40.07056, -2.93503), (40.30525, -3.04782),
                               (40.50898, -3.34639), (40.43686, -3.46864)))

        print_time = True
        prev_epoch = 0
        for i, master_line in enumerate(database):
            if i == 0:  # skip header
                continue
            data = master_line.split('\t')
            epoch_now = float(data[0])
            icao0 = str(data[2])

            if epoch_now < prev_epoch:
                # database going backwards, could be that raw data was already corrupt
                continue
            prev_epoch = epoch_now

            if epoch_now % 3600 == 0:
                if print_time:
                    print time_string(epoch_now) + ' ...'
                    print_time = False
            else:
                print_time = True

            if icao_filter is not None and icao0 != icao_filter:
                continue

            if icao0 not in icao_dict.keys():
                icao_dict[icao0] = Aircraft(icao0, epoch_now)
            current_aircraft = icao_dict[icao0]
            current_aircraft.last_seen = epoch_now

            call = str(data[3]).strip()
            if call:  # call found in or outside airport.
                if call+icao0 not in call_icao_list:  # record call+icao0 if seen more than once
                    call_icao_list.append(call+icao0)
                else:
                    current_aircraft.set_call(call, epoch_now)  # already fixes unknown call to op_timestamp
            current_flight = current_aircraft.get_current_flight(epoch_now)  # will be no_call flight if new

            if str(data[8]) and str(data[9]) and str(data[10]):
                current_aircraft.set_new_vel(epoch_now, float(data[8]), float(data[9]), float(data[10]))

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
                    # # TODO include ground positions in analysis. If QNH not properly applied, a higher surface pos will make it think it was a missed apprach
                    # continue
                    alt_uncorrected = airport_altitude  # ground position. Will be corrected but doesn't really matter
                    FL = 20
                if FL is not None and FL < 130:  # FL130
                    pos = Point(lat, lon)

            if pos is not None and TMA.contains(pos):

                NorS = None
                EorW = None
                ttrack = None
                gs = None
                inclin = None
                poly = None
                vrate = None
                found_data = False

                current_aircraft.set_new_pos(epoch_now, lat, lon, alt_uncorrected)
                # prev20_5_pos = current_aircraft.get_position_delimited(epoch_now, 5, 20)
                prev_vel = current_aircraft.get_velocity_delimited(epoch_now, 0, 20)
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
                        current_flight.set_guess(epoch_now, 'S', 'E', ttrack, vrate, inclin, gs, 4)
                    elif poly_SW.contains(pos):
                        current_flight.set_guess(epoch_now, 'S', 'W', ttrack, vrate, inclin, gs, 4)
                    elif poly_NE.contains(pos):
                        current_flight.set_guess(epoch_now, 'N', 'E', ttrack, vrate, inclin, gs, 4)
                    elif poly_NW.contains(pos):
                        current_flight.set_guess(epoch_now, 'N', 'W', ttrack, vrate, inclin, gs, 4)

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
                            prev30_10_pos = current_aircraft.get_position_delimited(epoch_now, 10, 30)
                            if prev30_10_pos is not None:  # can happen there was no prev data
                                prev_alt_corr = prev30_10_pos.alt - current_diff
                                prev_epoch = prev30_10_pos.epoch
                                # current_flight.operation.set_alt_ths_timestamp(epoch_now, prev_epoch, alt_corr, prev_alt_corr, NorS)

                            zone = int(poly[1])
                            current_flight.set_guess(epoch_now, NorS, EorW, ttrack, vrate, inclin, gs, zone)