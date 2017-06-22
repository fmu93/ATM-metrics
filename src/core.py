import extract_data
import main_gui
import threading
import analysis

no_call = 'no_call'
miss_event = 'missed? '
airport_altitude = 600
guess_alt_ths = 1800  # [m] above airport to discard flyovers
horHeaders = ['call', 'icao', 'type', 'opTimestamp','opTimestampDate','V(fpm)','GS(kts)','(deg)',
              'track','runway','change_comment','miss_comment','op_comment']


# output parameters
out_name = 'runway_allocation_'


class DataExtractorThread(threading.Thread):
    def __init__(self, infiles, ui):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.daemon = True
        self.infiles = infiles
        self.ui = ui
        self.icao_dict = {}
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.extract_data = extract_data.Metrics(self)

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()

    def task(self):
        # TODO list and order input files to feed the extract_data.py
        # display name of current database running
        for infile in self.infiles:
            print infile.name
            self.extract_data.run(infile, None)


class OperationRefreshThread(threading.Thread):
    """Thread that executes a task every N seconds"""

    def __init__(self, dataExtractor, ui):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.daemon = True
        self._interval = 3
        self.ui = ui
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
        print 'Refreshing ' + str(len(self.operation_dict.keys()))
        new_op_list = []
        for aircraft in self.dataExtractor.icao_dict.values():
            for flight in aircraft.flight_dict.values():
                if len(flight.operations) > 0 and \
                                flight.operations[-1].last_op_guess > flight.operations[-1].last_validation:

                    for operation in flight.get_operations(self.dataExtractor.extract_data.epoch_now):
                        if operation.op_runway or operation.op_timestamp is not None:
                            # final_operations_list.append(operation)
                            self.operation_dict[operation] = operation
                            new_op_list.append(operation)
        self.display()
        new_op_list.sort()
        for op in new_op_list:
            print op.get_op_rows()

    def display(self):
        op_list = []
        for op in (self.operation_dict.values()):
            op_list.append(op)
        op_list.sort(reverse=True)
        self.ui.dataToTable(op_list)


class Core:
    def __init__(self):
        self.dataExtractor = None
        self.operationRefresh = None
        self.ui = None
        self.infiles = [file('C:/Users/Croket/Python workspace/ATM metrics/data/digest_20160812dump1090.hex'),
                   file('C:/Users/Croket/Python workspace/ATM metrics/data/digest_20160813dump1090.hex')]

    def run(self):
        self.dataExtractor = DataExtractorThread(self.infiles, self.ui)
        self.operationRefresh = OperationRefreshThread(self.dataExtractor, self.ui)
        dataExtractorThread = threading.Thread(target=self.dataExtractor.run, args=())
        operationRefreshThread = threading.Thread(target=self.operationRefresh.run, args=())
        dataExtractorThread.start()
        operationRefreshThread.start()

    def stop(self):
        try:
            self.dataExtractor.shutdown()
            self.operationRefresh.shutdown()
            print 'killed!'
        except Exception:
            raise NameError('Can\'t kill threads')

    def set_ui(self, ui):
        self.ui = ui
        self.ui.tableWidget.setHorizontalHeaderLabels(horHeaders)
        self.ui.tableWidget.resizeColumnsToContents()

    def write_analysis(self):  # TODO write results to file like before
        op_list = []
        for op in self.operationRefresh.operation_dict.values():
            op_list.append(op)
        op_list.sort()
        analysis.FlightsLog('C:/Users/Croket/Python workspace/ATM metrics/data/',
                            'ra', op_list).write()
        print 'flights log saved'

# core Class
coreClass = Core()

if __name__ == '__main__':
    main_gui.run()
