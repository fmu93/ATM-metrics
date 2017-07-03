import time
import os


def time_string(epoch):
    "turns epoch time into a string: yyyy-mm-dd hh:mm:ss"
    if epoch is None:
        return "unknown_time"
    string = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(epoch)))
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

    def get_type(self, icao):
        if icao.upper() in self.icao_database.keys():
            return self.icao_database[icao.upper()][2]

    def get_regid(self, icao):
        if icao.upper() in self.icao_database.keys():
            return self.icao_database[icao.upper()][1]

icao_database = IcaoDatabase()
