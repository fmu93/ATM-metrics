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
            guess_log_file.write("call    \ticao  \ttype\topTimestamp\topTimestampDate \tV(fpm)\tGS(kts)\t(deg)\t"\
            "track\trunway\tchange_comment\tmiss_comment\top_comment\n")
            for operation in self.final_op_list:
                date = time_string(operation.op_timestamp)
                hour = time.gmtime(operation.op_timestamp).tm_hour
                if hour - prev_hour > 0 or hour - prev_hour <= -23:
                    guess_log_file.write('\n')
                try:
                    guess_log_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
                                         ('{:<8}'.format(operation.flight.callsign.call), '{:6}'.format(operation.flight.callsign.aircraft.icao),
                                          '{:4}'.format(operation.flight.callsign.aircraft.type), '{:.0f}'.format(operation.op_timestamp),
                                          date, '{:+05.0f}'.format(operation.get_mean_vrate()),
                                           '{:05.1f}'.format(operation.get_mean_gs()), '{:+04.1f}'.format(operation.get_mean_inclin()),
                                          '{:03.0f}'.format(operation.get_mean_track()), operation.op_runway, operation.zone_change_comment,
                                          operation.miss_comment, operation.op_comment))
                except Exception:
                    print 'Error in logging!!'
                prev_hour = hour


class ConfigLog:
    '''To crate a log file with the airport configuration. First time for a config start if the first take off in such
    configuration. Last time for a config end is the last landing in such config. Takes as input the final_guess_list'''

    def __init__(self, path, master_name, final_op_list):
        self.master_name = master_name
        self.path = path
        self.final_op_list = final_op_list
        self.logged_string = ''
        self.ops = ['32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R']  # for now no missed runway identification.   , '8L'+miss_event[0], '8R'+miss_event[0]]
        self.config_str = "From time\t\t\tUntil time\t\t\tCon\tTot\t"
        for op in self.ops:
            self.config_str += op + '\t'
        self.config_str += 'mis\tSlack capacity(min)\n'

    # def add_config(self, from_time, until_time, config, arr32L, arr32R, dep36L, dep36R, arr18L, arr18R, dep14L, dep14R, miss32L, miss32R, mis18L, mis18R):
    #     self.config_str = self.config_str + "%s\t%s\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (from_time, until_time, config, '{:d}'.format(arr32L), '{:d}'.format(arr32R),
    #                    '{:d}'.format(dep36L), '{:d}'.format(dep36R),  '{:d}'.format(arr18L), '{:d}'.format(arr18R),
    #                    '{:d}'.format(dep14L), '{:d}'.format(dep14R), '{:d}'.format(miss32L), '{:d}'.format(miss32R), '{:d}'.format(mis18L), '{:d}'.format(mis18R))
    #     return self.config_str
    def add_config(self, from_time, until_time, config, total, arr32L, arr32R, dep36L, dep36R, arr18L, arr18R, dep14L, dep14R, miss, slack):
        self.config_str = self.config_str + "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        from_time, until_time, config, '{:d}'.format(total), '{:d}'.format(arr32L), '{:d}'.format(arr32R),
        '{:d}'.format(dep36L), '{:d}'.format(dep36R), '{:d}'.format(arr18L), '{:d}'.format(arr18R),
        '{:d}'.format(dep14L), '{:d}'.format(dep14R), '{:d}'.format(miss), '{:.2f}'.format(slack))
        return self.config_str

    def write(self):
        # final_op_list = [[call, icao, typ, timestamp, performance, operation_comment, vrate, incli, gs, track], []...]
        log_file_name = '%s\\%s_configLog.txt' % (self.path, self.master_name)
        first_epoch = None
        last_conf = None
        config = None
        for operation in self.final_op_list:
            if operation.op_timestamp is not None and operation.val_operation_str:
                first_epoch = operation.op_timestamp
                if '32' in operation.val_operation_str or '36' in operation.val_operation_str:
                    last_conf = 'N'
                    config = 'N'
                else:
                    last_conf = 'S'
                    config = 'S'
                break

        from_time = time_string(first_epoch)
        last_epoch = self.final_op_list[-1].op_timestamp
        last_time = time_string(last_epoch)

        counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 32L, 32R, 36L, 36R, 18L, 18R, 14L, 14R...
        total_count = 0
        miss_count = 0
        prev_timestamp = 0
        prev_op = '-'
        log = False
        for operation in self.final_op_list:
            op_timestamp = operation.op_timestamp
            op = operation.val_operation_str

            if op_timestamp is not None and op and prev_op:
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
                    slack = (op_timestamp - prev_timestamp) / 60.0
                    self.add_config(from_time, until_time, config, total_count, counter[0], counter[1],
                                    counter[2], counter[3], counter[4], counter[5],
                                    counter[6], counter[7], miss_count, slack)
                    counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    total_count = 0
                    miss_count = 0
                    log = False
                    from_time = time_string(op_timestamp)  # first south op

                try:
                    total_count += 1
                    counter[self.ops.index(op)] += 1
                    if 'missed' in operation.op_comment:
                        miss_count += 1
                except Exception:
                    pass

                prev_timestamp = operation.op_timestamp
                prev_op = operation.val_operation_str

        self.add_config(from_time, last_time, last_conf, total_count, counter[0], counter[1],
                        counter[2], counter[3], counter[4], counter[5],
                        counter[6], counter[7], miss_count, slack=0)

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
