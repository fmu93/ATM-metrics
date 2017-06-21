import extract_data
import main_gui
import threading
import time

no_call = 'no_call'
miss_event = 'missed? '
airport_altitude = 600
guess_alt_ths = 1800  # [m] above airport to discard flyovers

# all new info extracted from database is modeled into aircraft, flight, operation...
icao_dict = {}
call_icao_list = []  # collect all calls+icao and validate those which appear more than once
operation_dict = {}

# output parameters
out_name = 'runway_allocation'


class DataExtractorThread(threading.Thread):
    def __init__(self, infiles):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self.extract_data = extract_data.Metrics()
        self.infiles = infiles

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

    def __init__(self):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = 10.0

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
        print 'Refreshing'
        print icao_dict.values()
        for aircraft in icao_dict.values():
            for flight in aircraft.flight_dict.values():
                if len(flight.operations) > 0 and \
                                flight.operations[-1].last_op_guess > flight.operations[-1].last_validation:

                    for operation in flight.get_operations():
                        if operation.val_operation_str or operation.op_timestamp is not None:
                            # final_operations_list.append(operation)
                            print operation


if __name__ == '__main__':

    infiles = [file('C:/Users/Croket/Python workspace/ATM metrics/data/digest_20160812dump1090.hex')]

    dataExtractor = DataExtractorThread(infiles)
    operationRefresh = OperationRefreshThread()

    dataExtractorThread = threading.Thread(target=dataExtractor.run, args=())
    operationRefreshThread = threading.Thread(target=operationRefresh.run, args=())

    dataExtractorThread.start()
    operationRefreshThread.start()


    # main_gui.run()
    # main_gui.Ui_Form.pushButton.clicked.connect(method)
