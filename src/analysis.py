from p_tools import time_string
from operator import itemgetter
import time


class FlightsLog:
    '''writes into file the final_guess_list of the operation analysis'''

    def __init__(self, path, name, final_op_list):
        self.path = path
        self.name = name
        self.final_op_list = final_op_list

    def write(self):
        log_file_name = '%s\\%s_flightsLog.txt' % (self.path, self.name)
        prev_hour = 24

        with open(log_file_name, 'w') as guess_log_file:
            guess_log_file.write("call    \ticao  \ttype\topTimestamp\topTimestampDate \tguess_count\tV(fpm)\tGS(kts)\t(deg)\t"\
            "track\trunway\tchange_comment\tmiss_comment\top_comment\twaypoints\n")
            for operation in self.final_op_list:
                date = time_string(operation.op_timestamp)
                hour = time.gmtime(operation.op_timestamp).tm_hour
                if hour - prev_hour != 0:
                    guess_log_file.write('\n')
                try:
                    guess_log_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
                                         ('{:<8}'.format(operation.flight.callsign.call), '{:6}'.format(operation.flight.aircraft.icao),
                                          '{:4}'.format(operation.flight.aircraft.type), '{:.0f}'.format(operation.op_timestamp),
                                          date, '{:1}'.format(operation.guess_count),'{:+05.0f}'.format(operation.get_mean_vrate()),
                                           '{:05.1f}'.format(operation.get_mean_gs()), '{:+04.1f}'.format(operation.get_mean_inclin()),
                                          '{:03.0f}'.format(operation.get_mean_track()), operation.op_runway, operation.zone_change_comment,
                                          operation.miss_comment, operation.op_comment, ', '.join(operation.flight.waypoints)))
                except Exception:
                    print 'Error in logging!!'
                    guess_log_file.write('Error with logging ' + '{:6}'.format(operation.flight.aircraft.icao))
                prev_hour = hour


class ConfigLog:
    '''To crate a log file with the airport configuration. First time for a config start if the first take off in such
    configuration. Last time for a config end is the last landing in such config. Takes as input the final_guess_list'''

    def __init__(self, final_op_list):
        self.config_list = []  # [Config, ...]
        final_op_list.sort()
        self.final_op_list = final_op_list
        self.ops = ['32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R']

    def add_config(self, config, from_epoch, until_epoch, runway_list, missed):
        slack = 0.0
        if self.config_list:
            self.config_list[-1].slack = from_epoch - self.config_list[-1].until_epoch
        self.config_list.append(Config(config, from_epoch, until_epoch, runway_list, missed, slack))

    def write(self, path, master_name):
        log_file_name = '%s\\%s_configLog.txt' % (path, master_name)
        config_head = "From time\t\t\tUntil time\t\t\tDur(h)\tCon\tTot\t"
        for op in self.ops:
            config_head += op + '\t'
        config_head += 'mis\tSlack capacity(min)\n'

        self.run()
        string = ''
        for config in self.config_list:
            for item in config.listed():
                string += item + '\t'
            string = string[0:-2] + '\n'

        with open(log_file_name, 'w') as config_log:
            config_log.write(config_head + string)

    def run(self):
        if self.final_op_list:
            # final_op_list = [[operation], []...]
            first_epoch = None
            last_config = None
            config = None
            for operation in self.final_op_list:
                if operation.op_timestamp is not None and operation.op_runway:
                    first_epoch = operation.op_timestamp
                    if '32' in operation.op_runway or '36' in operation.op_runway:
                        last_config = 'N'
                        config = 'N'
                    else:
                        last_config = 'S'
                        config = 'S'
                    break

            from_epoch = first_epoch
            last_epoch = self.final_op_list[-1].op_timestamp
            until_epoch = last_epoch

            counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 32L, 32R, 36L, 36R, 18L, 18R, 14L, 14R...
            total_count = 0
            miss_count = 0
            prev_timestamp = 0
            prev_op = '-'
            log = False
            for operation in self.final_op_list:
                op_timestamp = operation.op_timestamp
                op = operation.op_runway

                if op_timestamp is not None and op and prev_op:
                    if '32' in op or '36' in op:  # now NORTH
                        if '18' in prev_op or '14' in prev_op:  # prev south
                            until_epoch = prev_timestamp
                            log = True
                            config = 'S'
                            last_config = 'N'

                    elif '18' in op or '14' in op:  # now SOUTH
                        if '32' in prev_op or '36' in prev_op:  # prev north
                            until_epoch = prev_timestamp
                            log = True
                            config = 'N'
                            last_config = 'S'

                    if log:
                        self.add_config(config, from_epoch, until_epoch, counter, miss_count)
                        counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                        total_count = 0
                        miss_count = 0
                        log = False
                        from_epoch = op_timestamp

                    try:
                        total_count += 1
                        counter[self.ops.index(op)] += 1
                        if operation.missed_detected:
                            miss_count += 1
                    except Exception:
                        print 'error in op_timestamp, type: ' + type(op_timestamp)  # doesnt make sense this here...

                    prev_timestamp = operation.op_timestamp
                    prev_op = operation.op_runway

            self.add_config(last_config, from_epoch, last_epoch, counter, miss_count)

        return sorted(self.config_list)


class Config:
    def __init__(self, config, from_epoch, until_epoch, runway_list, missed, slack):
        self.config = config
        self.from_epoch = from_epoch
        self.until_epoch = until_epoch
        self.duration = (self.until_epoch - self.from_epoch) / 3600.0
        self.runway_list = runway_list  # [] 32L, 32R, 36L, 36R, 18L, 18R, 14L, 14R
        self.missed = missed
        self.slack = slack

    def __lt__(self, other):
        return self.from_epoch < other.from_epoch

    def listed(self):
        return [time_string(self.from_epoch), time_string(self.until_epoch), '{:.2f}'.format(self.duration),
                self.config, '{:d}'.format(sum(self.runway_list)), '{:d}'.format(self.runway_list[0]),
                '{:d}'.format(self.runway_list[1]), '{:d}'.format(self.runway_list[2]),
                '{:d}'.format(self.runway_list[3]), '{:d}'.format(self.runway_list[4]),
                '{:d}'.format(self.runway_list[5]), '{:d}'.format(self.runway_list[6]),
                '{:d}'.format(self.runway_list[7]), '{:d}'.format(self.missed), '{:.2f}'.format(self.slack/60.0)]


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

class thru_histogram:
    def __init__(self):
        self.bin_size = 15  # minutes
