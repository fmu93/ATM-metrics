import numpy as np
import math
from shapely.geometry import Polygon
from shapely.geometry import Point
from geopy.distance import great_circle
import os
from operator import itemgetter
import time
from Tkinter import *
import tkFileDialog


def time_string(epoch):
    "turns epoch time into a string: yyyy-mm-dd hh:mm:ss"
    if epoch is None:
        return "unknown_time"
    epoch = float(epoch)
    string = '%s-%s-%s %s:%s:%s' % (
        '{:04d}'.format(time.gmtime(epoch).tm_year), '{:02d}'.format(time.gmtime(epoch).tm_mon),
        '{:02d}'.format(time.gmtime(epoch).tm_mday), '{:02d}'.format(time.gmtime(epoch).tm_hour),
        '{:02d}'.format(time.gmtime(epoch).tm_min), '{:02d}'.format(time.gmtime(epoch).tm_sec))
    return string


class IcaoDatabase:
    '''loads the latest icao_database in memory for getting type or regist number'''
    # TODO integrate the other database instead
    def __init__(self):
        self.icao_database = [[0, 0, 0, 0, 0, 0, 0]]
        with open('../resources/icao_database.txt', 'r') as icao_database:
            for icao_data_line in icao_database.readlines():
                self.icao_database.append(icao_data_line.split('>'))

    def get_type(self, icao):
        for icao_data_line in reversed(self.icao_database):
            if icao == icao_data_line[0]:
                return icao_data_line[4]

    def get_regist(self, icao):
        for icao_data_line in reversed(self.icao_database):
            if icao == icao_data_line[0]:
                return icao_data_line[1]


class Position:

    def __init__(self, lat, lon, alt, epoch):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.epoch = epoch


class Velocity:

    def __init__(self, epoch, vrate, gs, ttrack):
        self.vrate = vrate
        self.gs = gs
        self.ttrack = ttrack
        self.epoch = epoch


class TrackInegrator:
    '''At the time this class is unsued. It's purpose is to integrate track angles to determine when a holding
    operation is performed'''

    def __init__(self):
        self.integrator_list = [[0, 0, 0, 0, 0]]  # [call, icao, original, integrated track, last epoch]

    def set_track(self, call, icao, track, epoch):
        new = 1
        for j, line in enumerate(self.integrator_list):
            if call == line[0]:
                new = 0
                if epoch - line[3] < 300:  # 5 min max difference
                    self.integrator_list[j][3] += track - line[2]
                    self.integrator_list[j][4] = epoch
                    print line
                    if abs(self.integrator_list[3]) > 180:
                        print 'detected holding! for icao: %s' % icao
                    break
        if new:
            self.integrator_list.append([call, icao, track, 0, epoch])


class Performance2:

    def __init__(self, zones):
        self.zones = zones

    def get_operation(self):
        operation_str = None  # text guess
        for zone in self.zones:  # increasing zone 0 - 4
            if zone is not None:  # Zone class
                guess_str = zone.guess_class.guess_str
                if zone.UorD == 'D':
                    if miss_event in guess_str and 0 < zone.zone < 3:
                        operation_str = guess_str
                    if zone.zone > 0 and operation_str is not None:
                        if guess_str[0:2] == operation_str[0:2] and guess_str != operation_str:
                            # next zone guess has same runway but not side (or event)
                            operation_str += ' approach from ' + guess_str + ' at zone ' + str(zone.zone)
                            break
                    elif operation_str is None and zone.zone < 4:
                        operation_str = guess_str

                elif zone.UorD == 'U':
                    if not zone.is_miss:  # take off
                        if operation_str is not None and guess_str not in operation_str:
                            operation_str += ' departure towards ' + guess_str + ' at zone ' + str(zone.zone)
                            break  # TODO don't stack up performances
                        else:
                            operation_str = guess_str
                    elif zone.zone > 0:  # missed approach, but in zone 0 it gives trouble
                        operation_str = guess_str
        return operation_str


class ZoneTimes:
    def __init__(self, zone, guess_class, UorD, is_miss):
        self.zone = zone
        self.guess_class = guess_class
        self.UorD = UorD
        self.is_miss = is_miss
        self.last_op_guess = None
        self.times = 0
        self.unweighted_times = 0
        if self.zone == 1:
            self.weight = 1.5
        elif self.zone == 2:
            self.weight = 1.2
        else:
            self.weight = 1

    def set_zone_guess(self, epoch):
        # weighting happens here
        self.times += 1*self.weight
        self.unweighted_times += 1
        self.last_op_guess = epoch


class OpGuess:

    def __init__(self, guess_str, NorS, EorW, UorD, event):
        self.guess_str = guess_str
        self.NorS = NorS
        self.EorW = EorW
        self.UorD = UorD

        self.is_miss = event != ''
        self.zone_dict = {}
        self.last_op_guess = None

    def set_guess_zone(self, epoch, zone):
        if zone not in self.zone_dict.keys():
            self.zone_dict[zone] = ZoneTimes(zone, self, self.UorD, self.is_miss)
        self.zone_dict[zone].set_zone_guess(epoch)


class Operation:

    def __init__(self, flight):
        self.flight = flight
        self.op_guess_dict = {}
        self.track_allow_landing = 25  # +- 25 degree to compare track
        self.track_allow_takeoff = 50
        self.last_op_guess = None
        self.IorO = None  # In or Out of airport, Approach or Take-Off
        self.LorT = None  # basically same as IorO but only after validation
        self.min_times = 3
        self.vrate_list = []  # TODO vrate per op only or evaluate throughout zones?
        self.inclin_list = []
        self.gs_list = []
        self.track_list = []

        self.op_timestamp = None
        self.pref = None
        self.alt_ths_timestamp = None
        self.threshold = airport_altitude + 600  # m
        self.val_operation_str = ''
        self.op_comment = ''

    def set_op_guess(self, epoch, NorS, EorW, track, vrate, inclin, gs, zone):
        # check for time between guesses
        bypass = False
        # if 0 < zone < 4:
        #     # 7 min or more between guesses? not in zone 0 because of taxiing in this zone
        #     if self.last_op_guess is not None and epoch - self.last_op_guess > 420:
        #         # new operation for this flight
        #         self.flight.
        #
        #         if epoch - self.last_op_guess > 1800:
        #             # make call  no call
        #             self.flight.aircraft.set_call(no_call, epoch)
        #         elif not self.flight.has_second_operation:
        #             self.flight.has_second_operation = True
        #             self.flight.aircraft.set_call(self.flight.call + call_suffix, epoch)
        #             self.flight.aircraft.flight_dict[self.flight.call + call_suffix].is_second_operation = True
        #         else:
        #             # a second operation is claiming yet another second operation? Srsly...
        #             print '????? ' + self.flight.aircraft.icao + ' ' + self.flight.call + ' wants triple operation????'
        #             pass
        if zone == 4:
            # no track and only approach into consideration
            bypass = True

        # save interesting parameters for zones 1 an
        if 0 < zone < 3:
            self.vrate_list.append(vrate)
            self.inclin_list.append(inclin)
            self.gs_list.append(gs)
            self.track_list.append(track)

        track = track % 360  # Wrapping [0, 360] just in case
        if vrate > 0:
            UorD = 'U'
        else:
            UorD = 'D'
        # operation identified by this parameters
        runway = ''
        side = ''
        event = ''
        if NorS == 'N':
            # UorD ~ D180 or U360
            if (180 - self.track_allow_landing <= track <= 180 + self.track_allow_landing) or bypass:
                self.IorO = 'I'
                runway = '18'
                if EorW == 'W':
                    side = 'R'
                elif EorW == 'E':
                    side = 'L'
                if UorD == 'D':
                    # normal 18 op
                    pass
                elif inclin > -1 and 0 < zone < 3:
                    event = miss_event
            elif (360 - self.track_allow_takeoff <= track <= 360 or 0 <= track <= 0 + self.track_allow_takeoff)\
                    and not bypass:
                self.IorO = 'O'
                runway = '36'
                if EorW == 'W':
                    side = 'L'
                elif EorW == 'E':
                    side = 'R'

        elif NorS == 'S':
            # UorD ~ D320 or U140
            if (320 - self.track_allow_landing <= track <= 320 + self.track_allow_landing) or bypass:
                self.IorO = 'I'
                runway = '32'
                if EorW == 'W':
                    side = 'L'
                elif EorW == 'E':
                    side = 'R'
                if UorD == 'D':
                    # normal 32 op
                    pass
                elif inclin > -1 and 0 < zone < 3:
                    event = miss_event
            elif (140 - self.track_allow_takeoff <= track <= 140 + self.track_allow_takeoff) and not bypass:
                self.IorO = 'O'
                runway = '14'
                if EorW == 'W':
                    side = 'R'
                elif EorW == 'E':
                    side = 'L'

        if runway != '' and side != '':
            guess_str = runway + side
            self.op_comment = event
            # timestamp as close to zone 0, but not inside zone 0
            if 0 < zone < 4:
                self.last_op_guess = epoch
                self.set_timestamp(epoch, zone, UorD)

            if guess_str not in self.op_guess_dict.keys():
                self.op_guess_dict[guess_str] = OpGuess(guess_str, NorS, EorW, UorD, event)

            self.op_guess_dict[guess_str].set_guess_zone(epoch, zone)

        return self.op_timestamp

    def get_op_timestamp(self):
        return self.op_timestamp

    def set_timestamp(self, epoch, zone, UorD):
        #  Out/takeoff, keep first -> only save first time
        if self.IorO == 'O' and (self.op_timestamp is None or zone < self.pref):
            self.op_timestamp = epoch
            self.pref = zone
        #  In/landing, always overwrite as it gets lower zone
        elif self.IorO == 'I':
            self.op_timestamp = epoch

    def set_alt_ths_timestamp(self, epoch_now, prev_epoch, alt, prev_alt, half):
        sign = None
        if alt > self.threshold > prev_alt:
            sign = 0  # up
        elif alt < self.threshold < prev_alt:
            sign = 1  # dq
        if sign is not None:
            if self.alt_ths_timestamp is None:
                self.alt_ths_timestamp = round(prev_epoch + (epoch_now - prev_epoch) / (alt - prev_alt) * (self.threshold - prev_alt))
                # self.sign = sign
                # self.half = half
            else:
                # second self.alt_ths_timestamp. TODO Evaluate prev and actual sign and half
                pass

    def validate_operation(self):
        north_zones = [None, None, None, None, None]  # [Zone0, ...]
        north_weight = 0.0  # all times of north zones 0-3
        delN4 = True
        south_zones = [None, None, None, None, None]
        delS4 = True
        south_weight = 0.0
        for op_guess in self.op_guess_dict.values():
            for zone_class in op_guess.zone_dict.values():
                if zone_class.times <= self.min_times:
                    continue  # pass on weak guesses
                if op_guess.NorS == 'N':
                    if zone_class.zone < 4:  # dont weight for zone 4
                        north_weight += zone_class.times
                    if north_zones[zone_class.zone] is None:
                        north_zones[zone_class.zone] = zone_class
                    elif zone_class.times > north_zones[zone_class.zone].times:
                        # save only one zone, but each zone remembers which guess it was from
                        north_zones[zone_class.zone] = zone_class
                        if op_guess.UorD == 'D':
                            delN4 = False

                elif op_guess.NorS == 'S':
                    if zone_class.zone < 4:
                        south_weight += zone_class.times
                    if south_zones[zone_class.zone] is None:
                        south_zones[zone_class.zone] = zone_class
                    elif zone_class.times > south_zones[zone_class.zone].times:
                        south_zones[zone_class.zone] = zone_class
                        if op_guess.UorD == 'D':
                            delS4 = False

        # delete approach guesses if no indication of landing operation (op_guess.UorD == 'D')
        if delN4:
            del north_zones[4]
        if delS4:
            del south_zones[4]

        # compare weights of north vs south and hopefully delete one of the two
        chosen_half = None
        if north_weight >= 1.2*south_weight:  # south weights less than half of north, pick north
            chosen_half = north_zones
        elif south_weight > 1.2*north_weight:  # north weights less than half of south, pick south
            chosen_half = south_zones

        if chosen_half is not None:
            self.val_operation_str = Performance2(chosen_half).get_operation()
            if self.val_operation_str is not None and ('32' in self.val_operation_str or '18' in self.val_operation_str):
                self.LorT = 'L'
            elif self.val_operation_str is not None and ('36' in self.val_operation_str or '14' in self.val_operation_str):
                self.LorT = 'T'
        return self

    def get_mean_vrate(self):
        return 0.0 if len(self.vrate_list) == 0 else reduce(lambda x, y: x + y, self.vrate_list) / len(self.vrate_list)

    def get_mean_inclin(self):
        return 0.0 if len(self.inclin_list) == 0 else reduce(lambda x, y: x + y, self.inclin_list) / len(self.inclin_list)

    def get_mean_gs(self):
        return 0.0 if len(self.gs_list) == 0 else reduce(lambda x, y: x + y, self.gs_list) / len(self.gs_list)

    def get_mean_track(self):
        return 0.0 if len(self.track_list) == 0 else reduce(lambda x, y: x + y, self.track_list) / len(self.track_list)


class Flight:

    def __init__(self, call, aircraft, epoch):
        self.aircraft = aircraft
        self.call = call
        self.latest_time = epoch
        self.operations = []  # [Operation()]

    def set_latest_time(self, epoch):
        self.latest_time = epoch

    def set_guess(self, epoch, NorS, EorW, track, vrate, inclin, gs, zone):
        # check for time gap/new flight
        if epoch - self.latest_time > 600:
            # more than 10 minutes with no calls and new guess is showing up, make new 'no_call' flight
            self.aircraft.set_call(no_call, epoch)
            # don't forget to assign this new guess to the new flight
            # self.aircraft.get_current_flight().set_guess(epoch, NorS, EorW, track, vrate, inclin, gs, zone)
            return

        if not len(self.operations) > 0 or (len(self.operations) > 0 and
            self.operations[-1].last_op_guess is not None and epoch - self.operations[-1].last_op_guess > 420):
            # first guess of flight or new guess 7 minutes after latest op guess time, make new Operation
            self.operations.append(Operation(self))
        self.operations[-1].set_op_guess(epoch, NorS, EorW, track, vrate, inclin, gs, zone)
        return

    def get_operations(self):
        operation_list = []  # Operation TODO separate operation and comment
        if len(self.operations) == 1:
            operation_list.append(self.operations[0].validate_operation())  # one operation
        elif len(self.operations) > 1:  # several operations
            prev_LorT = ''
            for i in range(len(self.operations)):
                validated_op = self.operations[i].validate_operation()
                if i > 0:
                    if prev_LorT == 'L' and validated_op.LorT == 'L':
                        # two consecuent attempts to land
                        operation_list[i-1].op_comment += '(missed approach) '
                        if validated_op.op_timestamp is None or operation_list[i-1].op_timestamp is None:
                            pass
                        else:
                            validated_op.op_comment += '(second approach aft: ' +\
                                    '{:1.2f}'.format((validated_op.op_timestamp -
                                                      operation_list[i - 1].op_timestamp) / 60.0) + ' min) '
                    else:
                        validated_op.op_comment += '(second operation) '

                operation_list.append(validated_op)
                prev_LorT = validated_op.LorT
        return operation_list


class Aircraft:

    def __init__(self, icao, first_seen):
        self.icao = icao
        self.flight_dict = {}  # [call] Flight
        self.first_seen = first_seen
        self.last_seen = None
        self.current_kolls = None
        self.current_flight = None  # updated from set_call
        self.set_call(no_call, first_seen)
        self.pos_buffer_dict = {}  # [epoch] records all positions but only few minutes before
        self.vel_buffer_dict = {}  # [epoch]

    def set_call(self, call, epoch):
        # check if this new call is the one of a prev aircraft that didn't send its call
        if call == no_call:
            # current flight is 'no_call'
            if no_call in self.flight_dict.keys():
                # 'no call' flight existed already, update it
                self.flight_dict[call].set_latest_time(epoch)
            else:
                # new 'no call' flight
                self.current_flight = Flight(call, self, epoch)
                self.flight_dict[call] = self.current_flight
        elif call in self.flight_dict.keys():
            # call already seen before
            if no_call in self.flight_dict.keys():
                # No data for a few minutes, then aircraft is back but doesn't have a recent call so 'no call'
                # was added for a while until it's previous call appears again. TODO merge no_call with prev/current call
                # this can happen when ac sends call for the first time while docked and again more than half an
                # hour later after take off, so it's ok to not merge in this case
                # print self.icao + ' lost a call: ' + call + ' at ' + time_string(self.flight_dict[call].latest_time) + ' and is back at ' + time_string(epoch)
                self.flight_dict.pop(no_call, None)  # remove key of unknown call
                self.flight_dict[call].set_latest_time(epoch)
                pass
            else:
                # there are no previous 'no call' flights, simply update current flight
                self.flight_dict[call].set_latest_time(epoch)
        else:
            # new call
            if no_call in self.flight_dict.keys():
                # replace old 'no call' with new call TODO check time difference (don't update a very old 'no call)
                self.flight_dict[call] = self.flight_dict[no_call]
                self.flight_dict.pop(no_call, None)  # remove key of unknown call
                self.flight_dict[call].set_latest_time(epoch)
                self.flight_dict[call].call = call
            else:
                # there are no previous 'no call' flights before this new call
                self.current_flight = Flight(call, self, epoch)
                self.flight_dict[call] = self.current_flight
            # print self.icao + ' has new flight call: ' + call + ' at ' + time_string(epoch)

    def get_current_flight(self, epoch):
        # method called only when aircraft inside TMA (airport vicinity)
        # returns new flight 'no_call' if this aircraft had no call for several minutes
        latest_epoch = 0
        flight = None
        for key in self.flight_dict:
            # get latest of all calls. Could be 'no_call'
            if latest_epoch <= self.flight_dict[key].latest_time <= epoch:
                latest_epoch = self.flight_dict[key].latest_time
                # last seen within 20 minutes?
                if epoch - 1200 <= latest_epoch:
                    flight = self.flight_dict[key]

        if flight is None:
            self.set_call(no_call, epoch)
            flight = self.flight_dict[no_call]

        return flight

    def get_call(self, epoch):
        latest_epoch = 0
        call = no_call
        for key in self.flight_dict:
            # get latest of all calls. Could be 'no_call'
            if latest_epoch <= self.flight_dict[key].latest_time <= epoch:
                latest_epoch = self.flight_dict[key].latest_time
                # last seen within 20 minutes?
                if epoch - 1200 <= latest_epoch:
                    call = key
        return call

    def set_kolls(self, kolls):
        self.current_kolls = kolls

    def get_current_diff(self):
        current_diff = None
        if self.current_kolls is not None:
            current_diff = float(30 * (1013 - self.current_kolls))
        return current_diff

    def set_new_pos(self, epoch, lat, lon, alt):
        for key in sorted(self.pos_buffer_dict):
            if epoch - key > 300:
                self.pos_buffer_dict.pop(key, None)  # remove key for old position
        self.pos_buffer_dict[epoch] = Position(lat, lon, alt, epoch)

    def get_position_delimited(self, epoch, min_bound, max_bound):
        for key in sorted(self.pos_buffer_dict, reverse=True):
            if min_bound <= epoch - key <= max_bound:
                return self.pos_buffer_dict[key]

    def set_new_vel(self, epoch, vrate, gs, ttrack):
        for key in sorted(self.vel_buffer_dict):
            if epoch - key > 300:
                self.vel_buffer_dict.pop(key, None)  # remove key for old entry
        self.vel_buffer_dict[epoch] = Velocity(epoch, vrate, gs, ttrack)

    def get_velocity_delimited(self, epoch, min_bound, max_bound):
        for key in sorted(self.vel_buffer_dict, reverse=True):
            if min_bound <= epoch - key <= max_bound:
                return self.vel_buffer_dict[key]


class FlightsLog:
    '''writes into file the final_guess_list of the operation analysis'''
    # final_op_list = [call, icao, typ, time_stamp, performance, operation_comment, avg_vrate, avg_inclin, avg_hspeed, avg_op_track]

    def __init__(self, path, master_name, final_op_list):
        self.path = path
        self.master_name = master_name
        self.final_op_list = final_op_list

    def write(self):
        log_file_name = '%s\\%s_flightsLog.txt' % (self.path, self.master_name)
        prev_hour = 24

        with open(log_file_name, 'w') as guess_log_file:
            guess_log_file.write("call    \ticao  \ttype\top_timestamp\top_timestamp_date  \tV(fpm)\tGS(kts)\t(deg)\ttrack\toperation\tcomment\n")
            for guess_line in self.final_op_list:
                date = time_string(guess_line[3])
                hour = time.gmtime(guess_line[3]).tm_hour
                if hour - prev_hour > 0 or hour - prev_hour <= -23:
                    guess_log_file.write('\n')
                try:
                    guess_log_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
                                         ('{:<8}'.format(guess_line[0]), '{:6}'.format(guess_line[1]),
                                          '{:4}'.format(guess_line[2]), guess_line[3], date, '{:+05.0f}'.format(guess_line[6]),
                                           '{:05.1f}'.format(guess_line[8]), '{:+04.1f}'.format(guess_line[7]),
                                          '{:03.0f}'.format(guess_line[9]), guess_line[4], guess_line[5]))
                except:
                    pass
                prev_hour = hour


class ConfigLog:
    '''To crate a log file with the airport configuration. First time for a config start if the first take off in such
    configuration. Last time for a config end is the last landing in such config. Takes as input the final_guess_list'''

    def __init__(self, path, master_name, final_op_list):
        self.master_name = master_name
        self.path = path
        self.final_op_list = final_op_list
        self.logged_string = ''
        self.ops = ['32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R', miss_event]  # for now no missed runway identification.   , '8L'+miss_event[0], '8R'+miss_event[0]]
        self.config_str = "timestamp1\t\t\ttimestamp2\t\t\tconfig\t"
        for op in self.ops:
            self.config_str += op + '\t'
        self.config_str += '\n'

    # def add_config(self, from_time, until_time, config, arr32L, arr32R, dep36L, dep36R, arr18L, arr18R, dep14L, dep14R, miss32L, miss32R, mis18L, mis18R):
    #     self.config_str = self.config_str + "%s\t%s\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (from_time, until_time, config, '{:d}'.format(arr32L), '{:d}'.format(arr32R),
    #                    '{:d}'.format(dep36L), '{:d}'.format(dep36R),  '{:d}'.format(arr18L), '{:d}'.format(arr18R),
    #                    '{:d}'.format(dep14L), '{:d}'.format(dep14R), '{:d}'.format(miss32L), '{:d}'.format(miss32R), '{:d}'.format(mis18L), '{:d}'.format(mis18R))
    #     return self.config_str
    def add_config(self, from_time, until_time, config, arr32L, arr32R, dep36L, dep36R, arr18L, arr18R, dep14L, dep14R, miss):
        self.config_str = self.config_str + "%s\t%s\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        from_time, until_time, config, '{:d}'.format(arr32L), '{:d}'.format(arr32R),
        '{:d}'.format(dep36L), '{:d}'.format(dep36R), '{:d}'.format(arr18L), '{:d}'.format(arr18R),
        '{:d}'.format(dep14L), '{:d}'.format(dep14R), '{:d}'.format(miss))
        return self.config_str

    def write(self):
        # final_op_list = [[call, icao, typ, timestamp, performance, operation_comment, vrate, incli, gs, track], []...]
        log_file_name = '%s\\%s_configLog.txt' % (self.path, self.master_name)
        first_epoch = None
        last_conf = None
        config = None
        for final_guess in self.final_op_list:
            if final_guess[3] is not None and final_guess[4] is not None:
                first_epoch = final_guess[3]
                if '32' in final_guess[4] or '36' in final_guess[4]:
                    last_conf = 'N'
                    config = 'N'
                else:
                    last_conf = 'S'
                    config = 'S'
                break

        from_time = time_string(first_epoch)
        last_epoch = self.final_op_list[-1][3]
        until_time = time_string(last_epoch)
        last_time = time_string(last_epoch)

        prev_line = [0, 0, 0, 0, '']  # call, icao, type, timestamp, op
        counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 32L, 32R, 36L, 36R, 18L, 18R, 14L, 14R...
        log = False
        for i, line in enumerate(self.final_op_list):
            prev_timestamp = prev_line[3]
            prev_op = prev_line[4] if len(prev_line[4]) < 4 else prev_line[4][0:6]
            op_timestamp = line[3]
            op = line[4] if len(line[4]) < 4 else line[4][0:6]

            if op_timestamp is not None and op is not None and prev_op is not None:
                if '32' in op or '36' in op:  # now NORTH
                    if '18' in prev_op or '14' in prev_op:  # prev south
                        until_time = time_string(prev_timestamp)  # latest south op
                        log = True
                        config = 'S'
                        last_conf = 'N'
                        print 'change of configuration from south to north'

                elif '18' in op or '14' in op:  # now SOUTH
                    if '32' in prev_op or '36' in prev_op:  # prev north
                        until_time = time_string(prev_timestamp)
                        log = True
                        config = 'N'
                        last_conf = 'S'
                        print 'change of configuration from north to south'

                if log:
                    self.add_config(from_time, until_time, config, counter[0], counter[1],
                                    counter[2], counter[3], counter[4], counter[5],
                                    counter[6], counter[7], counter[8])
                    counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    log = False
                    from_time = time_string(op_timestamp)  # first south op

                try:
                    counter[self.ops.index(op[-3:])] += 1
                except:
                    pass
                prev_line = line

        self.add_config(from_time, last_time, last_conf, counter[0], counter[1],
                        counter[2], counter[3], counter[4], counter[5],
                        counter[6], counter[7], counter[8])

        with open(log_file_name, 'w') as config_log:
            config_log.write(self.config_str)


class OpByType:
    '''Outputs the airport operations only as a function of how many different aircraft types performed in a given
    final_guess_list'''

    def __init__(self, path, master_name, final_op_list):
        self.master_name = master_name
        self.path = path
        self.final_op_list = final_op_list

    def write(self):  # call, icao, type, timestamp, op
        log_file_name = '%s\\%s_opByTypeLog.txt' % (self.path, self.master_name)
        type_list = [[], []]  # [[types, , , ], [amount, , , ]]
        typ_list = []  # [[A, times], [A, times], ...]
        for line in self.final_op_list:
            if line[2] not in type_list[0]:
                type_list[0].append(line[2])

        type_list[1] = [0] * len(type_list[0])
        for line in self.final_op_list:
            for i, typ in enumerate(type_list[0]):
                if line[2] == typ:
                    type_list[1][i] += 1
                    break

        for i, typ in enumerate(type_list[0]):
            typ_list.append([typ, type_list[1][i]])
        typ_list = sorted(typ_list, key=itemgetter(1), reverse=True)

        with open(log_file_name, 'w') as op_by_type:
            op_by_type.write('%s\t%s\n\n' % ('AType', 'times'))
            for i, ele in enumerate(typ_list):
                op_by_type.write('%s\t%s\n' % (ele[0], ele[1]))


class Analyzer:
    '''this is the core class where all the rest are called from. First it finds the database to read and
    initializes the needed classes. The run function defines some key polygons (zones, sides, TMA, airport area),
    then calculates the interpolated vrate and track angle from the previous positions saved in the buffer and then
    evaluates the guess hypothesis depending on position, vrate and track angle. Also notice that the classes for the
    collection of callsigns, setting operation timestamps or saving QNH's to calculate an altitude difference correction
    are called. Altitude is already corrected before it is inputted in the timestamp setter.'''

    def __init__(self, file):
        self.filepath = file.name
        self.master_name = os.path.splitext(os.path.basename(self.filepath))[0]
        self.master_database = None
        self.icao_database = IcaoDatabase()

        self.icao_dict = {}  # [icao] Flight class
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.guess_alt_ths = 1800  # [m] above airport to discard flyovers
        self.generic_current_diff = 0.0

        global no_call
        no_call = 'no_call'
        global airport_altitude
        airport_altitude = 600
        global miss_event
        miss_event = 'missed?'
        # self.op32R = '32R'
        # self.op32L = '32L'
        # self.op36R = '36R'
        # self.op36L = '36L'
        # self.op14R = '14R'
        # self.op14L = '14L'
        # self.op18R = '18R'
        # self.op18L = '18L'

    def run(self, icao_filter):
        try:
            self.master_database = open(self.filepath, 'r')
        except:
            raise NameError('No valid input path')

        icao_filter = icao_filter

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
        for i, master_line in enumerate(self.master_database):
            if i == 0:  # header
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

            if icao0 not in self.icao_dict.keys():
                self.icao_dict[icao0] = Aircraft(icao0, epoch_now)
            current_aircraft = self.icao_dict[icao0]
            current_aircraft.last_seen = epoch_now

            call = str(data[3]).strip()
            if not call == '':  # call found in or outside airport.
                if call+icao0 not in self.call_icao_list:  # record call+icao0 if seen more than once
                    self.call_icao_list.append(call+icao0)
                else:
                    current_aircraft.set_call(call, epoch_now)  # already fixes unknown call to op_timestamp
            current_flight = current_aircraft.get_current_flight(epoch_now)  # will be no_call flight if new

            if not str(data[8]) == '' and not str(data[9]) == '' and not str(data[10]) == '':
                current_aircraft.set_new_vel(epoch_now, float(data[8]), float(data[9]), float(data[10]))

            if not data[16] == '':  # kollsman found
                current_aircraft.set_kolls(float(data[16]))

            pos = None
            if not data[4] == '' and not data[5] == '':  # latitude information
                lat = float(data[4])
                lon = float(data[5])
                FL = None
                alt_uncorrected = None
                if not data[6] == '':
                    FL = float(data[6])
                    alt_uncorrected = FL * 30.48  # m, no QNH correction
                elif not data[7] == '':  # should be "1"
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
                UorD = None
                zone = None
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

                    if alt_uncorrected <= self.guess_alt_ths + airport_altitude:
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

    def end(self):
        self.master_database.close()

        # for all flights get validated_operation
        final_op_list = []
        for aircraft in self.icao_dict.values():
            for flight in aircraft.flight_dict.values():  # TODO flight has several operations, return list of validations
                for operation in flight.get_operations():
                    if operation.val_operation_str is not None or operation.op_timestamp is not None:
                        operation_str = operation.val_operation_str
                        operation_comment = operation.op_comment
                        op_timestamp = operation.op_timestamp
                        avg_vrate = operation.get_mean_vrate()
                        avg_inclin = operation.get_mean_inclin()
                        avg_gs = operation.get_mean_gs()
                        avg_op_track = operation.get_mean_track()

                        if op_timestamp is not None:
                            call = '{:<7}'.format(flight.call)
                            typ = self.icao_database.get_type(aircraft.icao)
                            final_op_list.append([call, aircraft.icao, typ, op_timestamp, str(operation_str), operation_comment, avg_vrate, avg_inclin, avg_gs, avg_op_track])

        final_op_list = sorted(final_op_list, key=itemgetter(3))  # in reverse time order

        FlightsLog(os.path.dirname(self.filepath), self.master_name, final_op_list).write()
        ConfigLog(os.path.dirname(self.filepath), self.master_name, final_op_list).write()
        # OpByType(os.path.dirname(self.filepath), self.master_name, final_op_list).write()


class GUI:
    def __init__(self, master):
        # self.icao_filter = "3cca06"
        self.icao_filter = None
        self.infiles = None
        master.title("atm metrics")
        master.resizable(False, False)
        self.frame = Frame(master, relief=RIDGE, borderwidth=2)
        self.frame.pack()

        self.toplabel = Label(self.frame, text="This will analyse performance at LEMD from a digest database").grid(
            row=0, pady=4, padx=12)
        self.fileButton = Button(self.frame, text="Select database", command=self.file_dialog).grid(row=1, pady=8)
        self.label = Label(self.frame, text="-").grid(row=2, pady=8)
        self.runButton = Button(self.frame, text="Run analyser", command=self.run_analyser).grid(row=3, column=0, pady=2)
        self.entry_filter = Entry(self.frame).grid(row=4, pady=3, padx=1)

    def file_dialog(self):
        self.infiles = tkFileDialog.askopenfiles()
        if len(self.infiles) == 1:
            self.label = Label(self.frame, text=self.infiles[0].name).grid(row=2, pady=8, padx=5)
        else:
            self.label = Label(self.frame, text='Multiple files').grid(row=2, pady=8, padx=5)
        print 'Ready to analyse:'
        for infile in self.infiles:
            print infile.name
        print ''

    def run_analyser(self):
        for infile in self.infiles:
            print 'Analyzing ' + infile.name
            analyser = Analyzer(infile)
            analyser.run(self.icao_filter)
            analyser.end()
            print "Done with " + infile.name+ '\n'

        print "Done with all files!\n"


if __name__ == '__main__':
    root = Tk()
    b = GUI(root)
    root.mainloop()




