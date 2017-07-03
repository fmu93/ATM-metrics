import extract_data
import main_gui
import threading
import analysis

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
        self.core = core
        self.icao_dict = {}
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.extract_data = extract_data.Metrics(self)

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
        self.extract_data.stop()

    def run(self):
        if self._finished.isSet(): return
        self.task()

    def task(self):
        # TODO list and order input files to feed the extract_data.py
        for infile in self.infiles:
            # display name of current database running
            print infile.name
            self.core.controller.setCurrent(infile.name)
            # icao_filter = '4ca5bb'
            icao_filter = None
            self.extract_data.run(infile, icao_filter)
        self.core.done()  # TODO add progress bar

    def dispTime(self, timeStr):
        self.core.controller.setClock(timeStr)


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

                        for operation in flight.get_operations(self.dataExtractor.extract_data.epoch_now):
                            if operation.op_timestamp is not None:  # TODO why are some op_timestamp None?
                                # TODO make sure operations are properlly... if one validation makes one op but then it/
                                # was another one, both remain instead of overwritting
                                # final_operations_list.append(operation)
                                self.operation_dict[operation] = operation
                                new_op_list.append(operation)
        self.display()
        new_op_list.sort()
        print 'Refreshing ' + str(len(new_op_list)) + ' of ' + str(len(self.operation_dict.keys())) + ' flights:'

    def display(self):
        op_list = []
        for op in (self.operation_dict.values()):
            op_list.append(op)

        op_list.sort()
        config_list = analysis.ConfigLog(op_list).run()

        config_list.sort(reverse=True)
        self.core.controller.update_tableConfig(config_list)
        op_list.sort(reverse=True)
        self.core.controller.update_tableFlights(op_list)


class Core:  # TODO use builtin time formats
    def __init__(self):
        self.dataExtractor = None
        self.operationRefresh = None
        self.controller = None
        self.infiles = None

    def run(self):
        if self.infiles:
            self.dataExtractor = DataExtractorThread(self.infiles, self)
            self.operationRefresh = OperationRefreshThread(self.dataExtractor, self)
            dataExtractorThread = threading.Thread(target=self.dataExtractor.run, args=())
            operationRefreshThread = threading.Thread(target=self.operationRefresh.run, args=())
            dataExtractorThread.start()
            operationRefreshThread.start()
            self.controller.setHap('Running')
            self.controller.update_progressbar(0)

    def stop(self):
        try:
            self.dataExtractor.shutdown()
            self.operationRefresh.shutdown()
            print 'threads killed!'
            self.controller.setHap('Threads killed!')
        except Exception:
            print 'Can\'t kill threads'
            self.controller.setHap('Can\'t kill threads')

    def done(self):
        self.operationRefresh.shutdown()
        self.controller.setHap('Done')

    def set_controller(self, controller):
        self.controller = controller

    def write_analysis(self):
        op_list = []
        for op in self.operationRefresh.operation_dict.values():
            op_list.append(op)
        op_list.sort()
        # TODO add filenames to output
        analysis.FlightsLog('C:/Users/Croket/Python workspace/ATM metrics/data/',
                            'test_flights', op_list).write()
        analysis.ConfigLog(op_list).write('C:/Users/Croket/Python workspace/ATM metrics/data/', 'test_config')
        print 'flights log saved'

# core Class
coreClass = Core()

if __name__ == '__main__':
    main_gui.run()
