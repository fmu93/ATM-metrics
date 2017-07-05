import os
import extract_data
import main_gui
import threading
import analysis
from p_tools import sortedDictKeys, get_file_name

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
        self.setName("DataExtractorThread")
        self.infiles = infiles
        self.infiles_dict = {}
        self.core = core
        self.icao_dict = {}
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.extract_data = extract_data.Metrics(self)
        self.num_lines = 1.0
        self.first_file = None
        self.file_count = 1
        self.forced_exit = False

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
                    self.infiles_dict[first_timestamp] = infile
                    self.num_lines += sum(1.0 for line in database)
                except:
                    print 'Error in file: ' + infile.name

        for timestamp in sortedDictKeys(self.infiles_dict):
            # display name of current database running
            if not self.first_file:
                self.first_file = self.infiles_dict[timestamp]
            print self.infiles_dict[timestamp].name
            self.core.controller.threadSample.setCurrent('File %d/%d: %s'
                                            % (self.file_count, len(self.infiles_dict),
                                               get_file_name(self.infiles_dict[timestamp])))
            # icao_filter = '4ca5bb'
            icao_filter = None
            self.extract_data.run(self.infiles_dict[timestamp], icao_filter)
            self.file_count += 1
        if not self.forced_exit:
            self.core.done()

    def dispTime(self, timeStr):
        self.core.controller.threadSample.setClock(timeStr)


class OperationRefreshThread(threading.Thread):
    """Thread that executes a task every N seconds"""

    def __init__(self, dataExtractor, core):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.setDaemon(True)
        self.setName("OperationRefreshThread")
        self._interval = 3
        self.core = core
        self.dataExtractor = dataExtractor
        self.operation_dict = {}

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

            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

    def task(self):
        """The task done by this thread - override in subclasses"""
        new_op_list = []
        for aircraft in self.dataExtractor.icao_dict.values():
                for flight in aircraft.flights_dict.values():
                    if len(flight.operations) > 0 and \
                                    flight.operations[-1].last_op_guess >= flight.operations[-1].last_validation:
                        # only compute/validate operation of aircraft which had a new guess from last validation
                        for operation in flight.get_operations(self.dataExtractor.extract_data.epoch_now):
                            if operation.op_timestamp is not None:  # TODO why are some op_timestamp None?
                                # TODO make sure operations are properly computed... if one validation makes one op but then it/
                                # was another one, both remain instead of overwritting
                                # final_operations_list.append(operation)
                                self.operation_dict[operation] = operation
                                new_op_list.append(operation)
        self.display()
        new_op_list.sort()
        # print 'Refreshing ' + str(len(new_op_list)) + ' of ' + str(len(self.operation_dict.keys())) + ' flights:'

    def display(self):
        op_list = []
        for op in (self.operation_dict.values()):
            op_list.append(op)

        if len(op_list) > 2:
            op_list.sort()
            config_list = analysis.ConfigLog(op_list).run()  # TODO make efficient analysis for 'only new'

            config_list.sort(reverse=True)
            self.core.controller.threadSample.update_tableConfig(config_list)
            op_list.sort(reverse=True)
            # small efficiency trick
            self.core.controller.threadSample.update_tableFlights(
                op_list[0:self.core.operations_table_rows] if len(op_list) > self.core.operations_table_rows else op_list)
            self.core.controller.histo.update_figure(op_list, config_list)


class Core:
    def __init__(self):
        self.dataExtractor = None
        self.operationRefresh = None
        self.controller = None
        self.infiles = None
        self.operations_table_rows = 200

    def run(self):
        if self.infiles:
            self.dataExtractor = DataExtractorThread(self.infiles, self)
            self.operationRefresh = OperationRefreshThread(self.dataExtractor, self)
            dataExtractorThread = threading.Thread(target=self.dataExtractor.run, args=())
            operationRefreshThread = threading.Thread(target=self.operationRefresh.run, args=())
            dataExtractorThread.start()
            operationRefreshThread.start()
            self.controller.threadSample.setHap('Running')
            self.controller.threadSample.update_progressbar(0)

    def stop(self):  # TODO make pause/resume button
        try:
            self.dataExtractor.shutdown()
            self.operationRefresh.shutdown()
            print 'threads killed!'
            self.controller.threadSample.setHap('Threads killed!')
        except Exception:
            print 'Can\'t kill threads'
            self.controller.threadSample.setHap('Can\'t kill threads')

    def done(self):
        self.operationRefresh.shutdown()
        self.controller.threadSample.setHap('Done')
        # self.controller.threadSample.update_progressbar(100)

    def set_controller(self, controller):
        self.controller = controller

    def write_analysis(self):
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

# core Class
coreClass = Core()

if __name__ == '__main__':
    main_gui.run()
