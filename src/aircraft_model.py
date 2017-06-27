from p_tools import icao_database, time_string, sortedDictKeys
from core import no_call, airport_altitude
from geo_resources import runway_ths_dict
from geopy.distance import great_circle
import operator
import time


class Aircraft:
    def __init__(self, icao, first_seen):
        self.icao = icao
        self.flights_dict = {}  # [Callsign] Flights
        self.set_call(no_call, first_seen)  # start off with no_call callsign
        self.first_seen = first_seen
        self.last_seen = None
        self.current_kolls = None
        self.last_kolls = None
        self.pos_buffer_dict = {}  # [epoch] records all positions but only few minutes before
        self.vel_buffer_dict = {}  # [epoch]
        self.type = icao_database.get_type(self.icao)
        self.regid = icao_database.get_regid(self.icao)

    def set_call(self, new_call, epoch):
        if not self.flights_dict.keys():
            self.flights_dict[Callsign(self, new_call, epoch)] = Flight(new_call, self, epoch)
            return

        current_callsign = sortedDictKeys(self.flights_dict)[-1]

        if current_callsign.call == new_call:
            # new call already in flight_dict.keys(). Same or new flight?
            if epoch - current_callsign.last_seen < 3600:  # same flight
                self.flights_dict[current_callsign].set_last_seen(epoch)
            else:  # new flight
                self.flights_dict[Callsign(self, new_call, epoch)] = Flight(new_call, self, epoch)

        elif current_callsign.call == no_call:
            if new_call == no_call:
                # current_callsign is no_call and another no_call shows up... treat as same?
                self.flights_dict[current_callsign].set_last_seen(epoch)
                return

            for callsign in self.flights_dict.keys():
                # check if this no_call is in between a previous callsign with same call
                if callsign.call == new_call and epoch - callsign.last_seen < 1800:
                    # no_call was splitting a same call for at most 30 min, ideally merge this no_call to prev call
                    self.flights_dict.pop(current_callsign, None)
                    self.flights_dict[callsign].set_last_seen(epoch)
                    return

            # move current_flight to a known call key
            new_callsign = Callsign(self, new_call, epoch)
            self.flights_dict[new_callsign] = self.flights_dict[current_callsign]
            self.flights_dict.pop(current_callsign, None)
            self.flights_dict[new_callsign].call = new_call
            self.flights_dict[new_callsign].set_last_seen(epoch)

        else:
            # simply a new different call
            self.flights_dict[Callsign(self, new_call, epoch)] = Flight(new_call, self, epoch)

    def get_current_flight(self):
        if self.flights_dict.keys():
            return self.flights_dict[sortedDictKeys(self.flights_dict)[-1]]

    def set_kolls(self, kolls, epoch):
        self.current_kolls = kolls
        self.last_kolls = epoch

    def get_current_diff(self):
        current_diff = 0
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


class Callsign:
    def __init__(self, aircraft, call, epoch):
        self.aircraft = aircraft
        self.call = call
        self.first_seen = epoch
        self.last_seen = epoch

    def __lt__(self, other):
        return self.first_seen < other.first_seen

    def set_last_seen(self, epoch):
        self.last_seen = epoch


class Flight:
    def __init__(self, call, aircraft, epoch):
        self.first_time = epoch
        self.aircraft = aircraft
        self.call = call
        self.last_seen = epoch
        self.operations = []  # [Operation()]
        self.waypoints = []  # ['waypoint_name', ...]

    def __lt__(self, other):
        return self.last_seen < other.last_seen  # to be able to sort

    def set_last_seen(self, epoch):
        self.last_seen = epoch

    def set_guess(self, epoch, NorS, EorW, track, vrate, inclin, gs, zone):
        # check for time gap/new flight
        if epoch - self.last_seen > 600:
            # more than 10 minutes with no calls and new guess is showing up, make new 'no_call' flight
            self.aircraft.set_call(no_call, epoch)
            # don't forget to assign this new guess to the new flight
            if self.aircraft.get_current_flight().call != no_call:
                # 'maximum recursion depth exceeded in cmp' when no_call
                self.aircraft.get_current_flight().set_guess(epoch, NorS, EorW, track, vrate, inclin, gs, zone)
            return

        if not len(self.operations) > 0 or (len(self.operations) > 0 and
            self.operations[-1].last_op_guess is not None and epoch - self.operations[-1].last_op_guess > 420):
            # first guess of flight or new guess 7 minutes after latest op guess time, make new Operation
            self.operations.append(Operation(self))
        self.operations[-1].set_op_guess(epoch, NorS, EorW, track, vrate, inclin, gs, zone)
        return

    def get_operations(self, epoch_now):
        operation_list = []  # Operation
        if len(self.operations) == 1:
            operation_list.append(self.operations[0].validate_operation(epoch_now))  # one operation
        elif len(self.operations) > 1:  # several operations
            prev_LorT = ''
            for i in range(len(self.operations)):
                validated_op = self.operations[i].validate_operation(epoch_now)
                if i > 0:
                    if prev_LorT == 'L' and validated_op.LorT == 'L':
                        # two consecutive attempts to land
                        operation_list[i-1].op_comment = '(first/2 approach) '
                        if validated_op.op_timestamp is None or operation_list[i-1].op_timestamp is None:
                            pass
                        else:
                            validated_op.op_comment = '(second approach aft: ' +\
                                    '{:1.2f}'.format((validated_op.op_timestamp -
                                                      operation_list[i - 1].op_timestamp) / 60.0) + ' min) '
                    else:
                        validated_op.op_comment = '(second operation) '  # with new callsign keying model we don't need this

                operation_list.append(validated_op)
                prev_LorT = validated_op.LorT
        return operation_list

    def set_waypoint(self, waypoint):
        if waypoint not in self.waypoints:
            self.waypoints.append(waypoint)


class Operation:

    def __init__(self, flight):
        self.flight = flight
        self.op_guess_dict = {}
        self.track_allow_landing = 25  # +- 25 degree to compare track
        self.track_allow_takeoff = 50
        self.last_op_guess = None
        self.last_validation = None
        self.IorO = None  # In or Out of airport, Approach or Take-Off
        self.LorT = None  # basically same as IorO but only after validation
        self.guess_count = 0
        self.min_times = 3
        self.vrate_list = []
        self.inclin_list = []
        self.gs_list = []
        self.track_list = []

        self.op_timestamp = None
        self.pref = None
        self.alt_ths_timestamp = 0
        self.threshold = airport_altitude + 800  # [m]     airport_altitude + 600  # m
        self.op_runway = ''
        self.op_comment = ''
        self.zone_change_comment = ''
        self.miss_comment = ''
        self.missed_detected = None
        self.miss_inclin_ths = 1
        self.miss_guess_count = 0
        self.miss_guess_min = 3

    def __lt__(self, other):
        return self.op_timestamp < other.op_timestamp  # to be able to sort

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
                    self.miss_guess_count = 0
                    pass
                elif inclin >= self.miss_inclin_ths and 0 < zone < 3:
                    # TODO distance to ths and alt at moment of missed... store first and wait until miss_count
                    self.miss_guess_count += 1
                    if self.missed_detected is None and self.miss_guess_count > self.miss_guess_min:
                        self.missed_detected = MissedApproach(self, epoch)
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
                    self.miss_guess_count = 0
                    pass
                elif inclin >= self.miss_inclin_ths and 0 < zone < 3:
                    # event = miss_event
                    self.miss_guess_count += 1
                    if self.missed_detected is None and self.miss_guess_count > self.miss_guess_min:
                        self.missed_detected = MissedApproach(self, epoch)
            elif (140 - self.track_allow_takeoff <= track <= 140 + self.track_allow_takeoff) and not bypass:
                self.IorO = 'O'
                runway = '14'
                if EorW == 'W':
                    side = 'R'
                elif EorW == 'E':
                    side = 'L'

        if runway != '' and side != '':
            guess_str = runway + side
            # timestamp as close to zone 0, but not inside zone 0
            if 0 < zone < 4:
                self.set_timestamp(epoch, zone, UorD)
                self.last_op_guess = epoch
                self.guess_count += 1

            if guess_str not in self.op_guess_dict.keys():
                self.op_guess_dict[guess_str] = OpGuess(guess_str, NorS, EorW, UorD, event)

            self.op_guess_dict[guess_str].set_guess_zone(epoch, zone)

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
        if alt > self.threshold > prev_alt or alt < self.threshold < prev_alt:
            self.alt_ths_timestamp = round(
                prev_epoch + (epoch_now - prev_epoch) / (alt - prev_alt) * (self.threshold - prev_alt))

        # sign = None
        # if alt > self.threshold > prev_alt:
        #     sign = 0  # up
        # elif alt < self.threshold < prev_alt:
        #     sign = 1  # dq
        # if sign is not None:
        #     if self.alt_ths_timestamp is None:
        #         self.alt_ths_timestamp = round(prev_epoch + (epoch_now - prev_epoch) / (alt - prev_alt) * (self.threshold - prev_alt))
        #         # self.sign = sign
        #         # self.half = half
        #     else:
        #         # second self.alt_ths_timestamp. TODO Evaluate prev and actual sign and half
        #         pass

    def validate_operation(self, epoch):
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
        chosen_half_zones = None
        if north_weight >= 1.2*south_weight:  # south weights less than half of north, pick north
            chosen_half_zones = north_zones
        elif south_weight > 1.2*north_weight:  # north weights less than half of south, pick south
            chosen_half_zones = south_zones

        if chosen_half_zones is not None:
            for zone in chosen_half_zones:  # increasing zone 0 - 4
                if zone is not None:  # Zone class
                    guess_str = zone.guess_class.guess_str
                    # landing
                    if zone.UorD == 'D':
                        if zone.guess_class.is_miss and 0 < zone.zone < 3:
                            self.op_runway = guess_str
                        if zone.zone > 0 and self.op_runway:
                            if guess_str[0:2] == self.op_runway[0:2] and guess_str != self.op_runway:
                                # next zone guess has same runway but not side (or event)
                                self.zone_change_comment = 'approach from ' + guess_str + ' at zone ' + str(zone.zone) + ' '
                                break
                        elif not self.op_runway and zone.zone < 4:
                            self.op_runway = guess_str
                    # take off
                    elif zone.UorD == 'U':
                        if not zone.is_miss:  # take off
                            if self.op_runway and guess_str not in self.op_runway:
                                self.zone_change_comment = 'departure towards ' + guess_str + ' at zone ' + str(zone.zone) + ' '
                                break  # TODO don't stack up performances
                            else:
                                self.op_runway = guess_str
                        elif zone.zone > 0:  # missed approach, but in zone 0 it gives trouble
                            self.op_runway = guess_str

            if self.op_runway is not None and ('32' in self.op_runway or '18' in self.op_runway):
                self.LorT = 'L'
            elif self.op_runway is not None and ('36' in self.op_runway or '14' in self.op_runway):
                self.LorT = 'T'

        self.last_validation = epoch
        return self

    def get_op_rows(self):
        return [self.flight.call, self.flight.aircraft.icao, self.flight.aircraft.type,
                ('{:.0f}'.format(self.op_timestamp) if self.op_timestamp else 'None'),
                time_string(self.op_timestamp), '{:1}'.format(self.guess_count), '{:4.0f}'.format(self.get_mean_vrate()), '{:3.0f}'.format(self.get_mean_gs()),
                '{:.1f}'.format(self.get_mean_inclin()), '{:3.0f}'.format(self.get_mean_track()), self.op_runway,
                self.zone_change_comment, self.miss_comment, self.op_comment, ', '.join(self.flight.waypoints)]

    def get_mean_vrate(self):
        return 0.0 if len(self.vrate_list) == 0 else reduce(lambda x, y: x + y, self.vrate_list) / len(self.vrate_list)

    def get_mean_inclin(self):
        return 0.0 if len(self.inclin_list) == 0 else reduce(lambda x, y: x + y, self.inclin_list) / len(self.inclin_list)

    def get_mean_gs(self):
        return 0.0 if len(self.gs_list) == 0 else reduce(lambda x, y: x + y, self.gs_list) / len(self.gs_list)

    def get_mean_track(self):
        return 0.0 if len(self.track_list) == 0 else reduce(lambda x, y: x + y, self.track_list) / len(self.track_list)


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


class MissedApproach:
    def __init__(self, operation, epoch):
        self.operation = operation
        self.operation.validate_operation(epoch)
        self.runway = self.operation.op_runway
        self.position = self.operation.flight.aircraft.get_position_delimited(epoch, 0, 5)
        self.alt = self.position.alt - self.operation.flight.aircraft.get_current_diff()
        self.timestamp = epoch
        self.dist_to_ths = None
        for runway_ths_key in runway_ths_dict.keys():
            if self.runway in runway_ths_key:
                self.dist_to_ths = great_circle((self.position.lat, self.position.lon),
                                                runway_ths_dict[runway_ths_key]).nautical
                break
        self.operation.miss_comment = '(missed @ ' + '{:1.0f}'.format(self.alt*100) + ' ft, ' +\
                                      '{:1.2f}'.format(self.dist_to_ths) + ' nm from ths) '

