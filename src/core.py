# from __future__ import with_statement
import os
import extract_data
import main_gui
import threading
import analysis
from p_tools import sortedDictKeys, get_file_name
from Queue import Queue

no_call = 'no_call'
miss_event = 'missed? '
airport_altitude = 600  # [m]
guess_alt_ths = 1800  # [m] above airport to discard flyovers

# output parameters
out_name = 'runway_allocation_'


class DataExtractorThread(threading.Thread):
    def __init__(self, infiles, core):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.setDaemon(True)
        self.infiles = infiles
        self.infiles_dict = {}
        self.core = core
        self.files_data_dict = {}
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.extract_data = extract_data.Metrics(self)
        self.num_lines = 0
        self.first_file = None
        self.file_count = 1
        self.forced_exit = False
        self.paused = False

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
        self.forced_exit = self.extract_data.stop()

    def run(self):
        if self._finished.isSet(): return
        self.task()

    def task(self):
        for infile in self.infiles:
            with open(infile.name, 'r') as database:
                try:
                    head = [database.readline() for x in xrange(2)]  # get first two lines (header + first)
                    first_timestamp = float(head[-1].split('\t')[0])
                    # dict of files with first timestamp as key
                    self.infiles_dict[first_timestamp] = infile
                    self.num_lines += sum(1.0 for line in database)
                except:
                    print 'Error in file: ' + infile.name

        for timestamp in sortedDictKeys(self.infiles_dict):
            # display name of current database running
            if not self.first_file:
                self.first_file = self.infiles_dict[timestamp]
            print self.infiles_dict[timestamp].name
            self.core.controller.setCurrent('File %d/%d: %s'
                                            % (self.file_count, len(self.infiles_dict),
                                               get_file_name(self.infiles_dict[timestamp])))
            # icao_filter = '4ca981'
            icao_filter = None
            self.files_data_dict[timestamp] = {}  # icao_dict
            self.extract_data.run(timestamp, self.infiles_dict[timestamp], icao_filter)
            self.file_count += 1
            # validate when finished
            self.core.validate(False)

        if not self.forced_exit:
            self.core.done()

    def dispTime(self, timeStr):
        self.core.controller.setClock(timeStr)


class OperationRefreshThread(threading.Thread):
    """Thread that executes a task every N seconds"""

    def __init__(self, dataExtractor, core, live_run):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.setDaemon(True)
        self.live_run = live_run
        self._interval = 10
        self.core = core
        self.dataExtractor = dataExtractor
        self.operation_dict = {}
        self.paused = False
        self.lock = threading.Lock()

    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()
            # finish if just wanted to run once
            if not self.live_run: return
            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

    def task(self):
        if not self.paused:
            with self.lock:
                """The task done by this thread - override in subclasses"""
                for icao_dict in self.dataExtractor.files_data_dict.values():
                    for aircraft in icao_dict.values():
                        for flight in aircraft.flights_dict.values():
                            if len(flight.operations) > 0 and \
                                            flight.operations[-1].last_op_guess >= flight.operations[-1].last_validation:
                                # only compute/validate operation of aircraft which had a new guess from last validation
                                for operation in flight.get_operations(self.dataExtractor.extract_data.epoch_now):
                                    if operation.get_op_timestamp():  # TODO why are some op_timestamp None?
                                        self.operation_dict[operation] = operation
                            # this will evaluate the waypoints (unefficient manner if it has to recompute all again)
                            flight.get_sid_star(self.dataExtractor.extract_data.epoch_now)

            if not self.core.is_light_run:
                self.display()

    def display(self):
        op_list = []
        for op in (self.operation_dict.values()):
            if (not self.core.model_filter or (op.flight.aircraft.model in self.core.model_filter)) and\
                (not self.core.airline_filter or (op.flight.aircraft.operator in self.core.airline_filter)) and\
                    (not self.core.config_filter or (op.config in self.core.config_filter)) and\
                    (not self.core.start_filter or (op.get_op_timestamp() >= self.core.start_filter)) and\
                    (not self.core.end_filter or (op.get_op_timestamp() <= self.core.end_filter)):

                op_list.append(op)

        if len(op_list) > -1:
            op_list.sort()
            config_list = analysis.ConfigLog(op_list).run()  # TODO make efficient analysis for 'only new'
            self.core.controller.update_tableConfig(config_list)
            # small efficiency trick
            self.core.controller.update_tableFlights(
                op_list[0:self.core.operations_table_rows] if len(op_list) > self.core.operations_table_rows else op_list,

                self.dataExtractor.extract_data.epoch_now)
            self.core.controller.histo.update_figure(op_list, config_list)


class Core:  # TODO does this have to be a class??
    def __init__(self):
        self.dataExtractor = None
        self.operationRefresh = None
        self.controller = None
        self.infiles = None
        self.operations_table_rows = 200
        self.console_text = ''
        self.is_light_run = False
        self.live_run = False
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        # queue to run functions from main thread TODO...
        self.q = Queue()
        # start/end times
        self.is_delimited = False
        self.analyseStart = None
        self.analyseEnd = None
        # filters
        self.evaluate_waypoints = True
        self.airline_filter = None
        self.model_filter = None
        self.config_filter = None
        self.start_filter = None
        self.end_filter = None

    def run(self):
        self.controller.disable_for_light(False)
        self.is_light_run = False
        self.start_analysis()

    def light_run(self):
        self.controller.disable_for_light(True)
        self.is_light_run = True
        self.start_analysis()

    def start_analysis(self):
        self.controller.disable_run(True)
        if self.infiles and not self.dataExtractor:
            self.dataExtractor = DataExtractorThread(self.infiles, self)
            dataExtractorThread = threading.Thread(target=self.dataExtractor.run, name='dataExtractor', args=())
            dataExtractorThread.start()
            if self.live_run:
                self.validate(self.live_run)
            self.controller.setHap('Running')
            with self.lock2:
                self.controller.update_progressbar(0)

    def validate(self, live_run):
        self.operationRefresh = OperationRefreshThread(self.dataExtractor, self, live_run)
        operationRefreshThread = threading.Thread(target=self.operationRefresh.run, name='operationRefresh', args=())
        operationRefreshThread.start()
        self.controller.setHap('Validating')

    def stop(self):
        try:
            self.dataExtractor.shutdown()
            self.dataExtractor = None
            self.controller.setHap('Data extraction terminated')
            self.operationRefresh.shutdown()
            self.operationRefresh = None
            print 'threads killed!',
            self.controller.setHap('Threads killed!')
            self.controller.update_progressbar(0)
        except Exception:
            print 'Can\'t kill threads'
            self.controller.setHap('Can\'t kill threads')
        self.controller.disable_run(False)

    def pause(self):
        if self.dataExtractor.paused:
            self.dataExtractor.paused = False
            self.operationRefresh.paused = False
            self.controller.setHap('Running')
            self.controller.ui.btnPause.setText('Pause')
        else:
            self.dataExtractor.paused = True
            self.operationRefresh.paused = True
            self.controller.setHap('threads paused')
            self.controller.ui.btnPause.setText('Resume')

    def done(self):
        self.dataExtractor.shutdown()
        self.operationRefresh.shutdown()
        self.write_analysis()
        self.dataExtractor = None
        self.controller.setHap('Done')
        # self.controller.update_progressbar(100)  # TODO this will hang the program!
        self.controller.disable_run(False)

    def set_controller(self, controller):
        self.controller = controller
        self.controller.disable_run(True)

    def make_display(self):
        if self.operationRefresh:
            self.operationRefresh.display()

    def write_analysis(self):
        with self.lock1:
            op_list = []
            for op in self.operationRefresh.operation_dict.values():
                op_list.append(op)
            op_list.sort()
            analysis.FlightsLog(os.path.dirname(self.dataExtractor.first_file.name),
                                os.path.splitext(os.path.basename(self.dataExtractor.first_file.name))[0],
                                op_list).write()
            analysis.ConfigLog(op_list).write(os.path.dirname(self.dataExtractor.first_file.name),
                                              get_file_name(self.dataExtractor.first_file))
        print 'logs saved'
        self.controller.print_console('logs saved')

# core Class
coreClass = Core()

if __name__ == '__main__':
    main_gui.run()
