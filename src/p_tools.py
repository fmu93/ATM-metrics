import time

no_call = 'no_call'
miss_event = 'missed? '
airport_altitude = 600

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
    def __init__(self):
        self.icao_database = {}
        with open('../resources/aircraft_db.csv', 'r') as icao_database:
            for icao_data_line in icao_database.readlines():
                # icao,regid,mdl,type,operator
                line = icao_data_line.split(',')
                self.icao_database[line[0].upper()] = line

    def get_type(self, icao):
        if icao.upper() in self.icao_database.keys():
            return self.icao_database[icao.upper()][2]

    def get_regid(self, icao):
        if icao.upper() in self.icao_database.keys():
            return self.icao_database[icao.upper()][1]

