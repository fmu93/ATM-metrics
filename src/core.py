import extract_data
import main_gui
import threading
import analysis

no_call = 'no_call'
miss_event = 'missed? '
airport_altitude = 600
guess_alt_ths = 1800  # [m] above airport to discard flyovers


# output parameters
out_name = 'runway_allocation'


class DataExtractorThread(threading.Thread):
    def __init__(self, infiles):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.infiles = infiles
        self.icao_dict = {}
        self.call_icao_list = []  # collect all calls+icao and validate those which appear more than once
        self.extract_data = extract_data.Metrics(self)

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def run(self):
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

    def __init__(self, dataExtractor):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = 5
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
        print 'Refreshing ' + str(len(self.dataExtractor.icao_dict.keys()))
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

        new_op_list.sort()
        for op in new_op_list:
            op.print_op()


def write_analysis():  # TODO write results to file like before
    # analysis.FlightsLog()
    pass


def run():
    infiles = [file('C:/Users/Croket/Python workspace/ATM metrics/data/digest_20160812dump1090.hex'),
               file('C:/Users/Croket/Python workspace/ATM metrics/data/digest_20160813dump1090.hex')]

    dataExtractor = DataExtractorThread(infiles)
    operationRefresh = OperationRefreshThread(dataExtractor)
    dataExtractorThread = threading.Thread(target=dataExtractor.run, args=())
    operationRefreshThread = threading.Thread(target=operationRefresh.run, args=())
    dataExtractorThread.start()
    operationRefreshThread.start()

if __name__ == '__main__':

    main_gui.run()
    # main_gui.Ui_Form.pushButton.clicked.connect(run())
