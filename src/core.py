# from __future__ import with_statement
import os
import extract_data
import main_gui
import threading
import analysis
from p_tools import sortedDictKeys, get_file_name
from Queue import Queue


class DataExtractorThread(threading.Thread):
    def __init__(self, infiles, core):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.setDaemon(True)
        self.infiles = infiles
        self.infiles_dict = {}
        self.core = core
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.extract_data = extract_data.Metrics(self)
        self.num_lines = 0
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
                except Exception:
                    print 'Error in file: ' + infile.name
                    self.core.controller.print_console('Error in file: ' + infile.name)

        for timestamp in sortedDictKeys(self.infiles_dict):
            # display name of current database running
            if not self.core.first_file_name:
                self.core.first_file_name = self.infiles_dict[timestamp].name
            print self.infiles_dict[timestamp].name
            self.core.controller.setCurrent('File %d/%d: %s'
                                            % (self.file_count, len(self.infiles_dict),
                                               get_file_name(self.infiles_dict[timestamp])))
            icao_filter = '343147'
            # icao_filter = None
            self.core.files_data_dict[timestamp] = {}  # icao_dict
            self.extract_data.run(timestamp, self.infiles_dict[timestamp], icao_filter)
            self.file_count += 1
            # validate when finished with each file
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
        self.core = core
        self.dataExtractor = dataExtractor
        self.paused = False
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()

    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def run(self):
        while 1:
            if self._finished.isSet():
                return
            self.task()
            # finish if just wanted to run once and write analysis
            if not self.live_run:
                self.core.write_analysis(False)
                return
            # sleep for interval or until shutdown
            self._finished.wait(self.core.refreshRate)

    def task(self):
        if not self.paused:
            with self.lock1:
                """The task done by this thread - override in subclasses"""
                for icao_dict in self.core.files_data_dict.values():
                    for aircraft in icao_dict.values():
                        for flight in aircraft.flights_dict.values():
                            if len(flight.operations) > 0 and \
                                            flight.operations[-1].last_op_guess >= flight.operations[-1].last_validation:
                                # only compute/validate operation of aircraft which had a new guess from last validation
                                for operation in flight.get_operations(self.dataExtractor.extract_data.epoch_now):
                                    if operation.get_op_timestamp():  # TODO why are some op_timestamp None?
                                        self.core.operation_dict[operation] = operation
                            # this will evaluate the waypoints (unefficient if it has to recompute all again while in "refresh" mode)
                            flight.get_sid_star(self.dataExtractor.extract_data.epoch_now)

            if not self.core.is_light_run:
                self.display()

    def display(self):
        op_list = []
        with self.lock2:
            for op in (self.core.operation_dict.values()):
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
                self.core.controller.update_tableFlights(op_list, self.dataExtractor.extract_data.epoch_now)

                self.core.controller.update_histo(op_list, config_list)


class Core:  # TODO does this have to be a class??
    def __init__(self):
        self.dataExtractor = None
        self.operationRefresh = None
        self.controller = None
        self.infiles = None
        self.operations_table_rows = 200
        self.console_text = ''
        self.is_live_run = False
        self.is_light_run = False
        self.refreshRate = 5
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
        # results
        self.files_data_dict = {}
        self.operation_dict = {}
        self.first_file_name = ''
        # out files
        self.out_name = ''

    def run(self):
        # self.controller.disable_for_light(False)
        self.is_live_run = False
        self.start_analysis()

    def live_run(self):
        # self.controller.disable_for_light(True)
        self.is_live_run = True
        self.start_analysis()

    def start_analysis(self):
        self.files_data_dict = {}
        self.operation_dict = {}
        self.controller.disable_run(True)
        self.controller.disable_stop_pause(False)
        if self.infiles and not self.dataExtractor:
            self.dataExtractor = DataExtractorThread(self.infiles, self)
            dataExtractorThread = threading.Thread(target=self.dataExtractor.run, name='dataExtractor', args=())
            dataExtractorThread.start()
            if self.is_live_run:
                self.validate(self.is_live_run)
            self.controller.setHap('Running')
            self.controller.update_progressbar(0)

    def validate(self, live_run):
        self.operationRefresh = OperationRefreshThread(self.dataExtractor, self, live_run)
        operationRefreshThread = threading.Thread(target=self.operationRefresh.run, name='operationRefresh', args=())
        operationRefreshThread.start()

    def stop(self):
        try:
            self.dataExtractor.shutdown()
            self.dataExtractor = None
            self.controller.setHap('Data extraction terminated')
            if self.operationRefresh:
                self.operationRefresh.shutdown()
                self.operationRefresh = None
                self.controller.setHap('Threads killed!')
            self.controller.update_progressbar(0)
        except Exception:
            print 'Can\'t kill threads'
            self.controller.setHap('Can\'t kill threads')
        self.controller.disable_run(False)

    def pause(self):
        if self.dataExtractor.paused:
            self.dataExtractor.paused = False
            if self.operationRefresh:
                self.operationRefresh.paused = False
            self.controller.setHap('Running')
            self.controller.ui.btnPause.setText('Pause')
        else:
            self.dataExtractor.paused = True
            if self.operationRefresh:
                self.operationRefresh.paused = True
            self.controller.setHap('threads paused')
            self.controller.ui.btnPause.setText('Resume')

    def done(self):
        self.dataExtractor.shutdown()
        self.operationRefresh.shutdown()
        self.dataExtractor = None
        self.controller.setHap('Done')
        # self.controller.update_progressbar(100)  # TODO if set to 100 the program will hang!!!!
        self.controller.disable_run(False)

    def set_controller(self, controller):
        self.controller = controller
        self.controller.disable_run(True)
        self.controller.disable_stop_pause(True)

    def make_display(self):
        if self.operationRefresh:
            self.operationRefresh.display()

    def write_analysis(self, validate):
        if validate:
            self.validate(False)
        with self.lock1:
            if self.out_name:
                out_name = self.out_name
            else:
                out_name = os.path.splitext(os.path.basename(self.first_file_name))[0]

            op_list = [op for op in self.operation_dict.values()]
            op_list.sort()
            analysis.FlightsLog(op_list).write(os.path.dirname(self.first_file_name), out_name)
            analysis.ConfigLog(op_list).write(os.path.dirname(self.first_file_name), out_name)
        print 'logs saved'
        self.controller.print_console('logs saved')

# core Class
coreClass = Core()

if __name__ == '__main__':
    main_gui.run()
