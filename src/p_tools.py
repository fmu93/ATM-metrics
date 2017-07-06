import time
import os


def time_string(epoch):
    "turns epoch time into a string: yyyy-mm-dd hh:mm:ss"
    if epoch is None:
        return "unknown_time"
    string = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(epoch)))
    return string


def duration_string(seconds):
    if seconds is None:
        return "unknown duration"
    if seconds > 86400:
        days = int(seconds / 86400)
        seconds = seconds - days*86400
        string = '%sd %s:%s:%s' % (days, '{:02.0f}'.format(seconds / 3600),
                                   '{:02.0f}'.format((seconds % 3600) / 60),
                                   '{:02.0f}'.format((seconds % 3600) % 60))
    else:
        string = '%s:%s:%s' % ('{:02.0f}'.format(seconds / 3600),
                               '{:02.0f}'.format((seconds % 3600) / 60),
                               '{:02.0f}'.format((seconds % 3600) % 60))
    return string


def get_file_name(infile):
    return os.path.splitext(os.path.basename(infile.name))[0]


def sortedDictKeys(adict):
    keys = adict.keys()
    keys.sort()
    return [key for key in keys]


class IcaoDatabase:
    '''loads the latest icao_database in memory for getting type or regist number'''
    def __init__(self):
        self.icao_database = {}
        with open('../resources/aircraft_db.csv', 'r') as icao_database:
            for icao_data_line in icao_database.readlines():
                # icao,regid,mdl,type,operator
                line = icao_data_line.split(',')
                self.icao_database[line[0].upper()] = line

    def get_mdl(self, icao):
        mdl = 'None'
        if icao.upper() in self.icao_database.keys():
            mdl = self.icao_database[icao.upper()][2]
        return mdl

    def get_regid(self, icao):
        regid = 'None'
        if icao.upper() in self.icao_database.keys():
            regid = self.icao_database[icao.upper()][1]
        return regid

    def get_operator(self, icao):
        operator = 'None'
        if icao.upper() in self.icao_database.keys():
            operator = self.icao_database[icao.upper()][4].replace('\n', '')
        return operator

    # TODO get list of unique operators

icao_database = IcaoDatabase()
