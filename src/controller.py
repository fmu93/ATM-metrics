import core
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

flight_headers = ['call', 'icao', 'type', 'opTimestamp','opTimestampDate','pos_count','V(fpm)','GS(kts)','(deg)',
              'track','runway','change_comm','miss_comm','op_comm', 'waypoints']
config_headers = ['From time', 'Until time', 'Dur (h)', 'Config', 'Total', '32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R',
                  'missed', 'Slack (min)']


class Controller:
    def __init__(self, ui):
        self.core = core.coreClass
        self.ui = ui
        self.setTable()
        self.connections()
        self.set_palette()
        self.core.set_controller(self)

    def setTable(self):
        self.ui.tableFlights.setColumnCount(15)
        self.ui.tableFlights.setRowCount(200)
        self.ui.tableFlights.setHorizontalHeaderLabels(flight_headers)
        self.ui.tableFlights.resizeColumnsToContents()
        self.ui.tableConfig.setColumnCount(15)
        self.ui.tableConfig.setRowCount(5)
        self.ui.tableConfig.setHorizontalHeaderLabels(config_headers)
        self.ui.tableConfig.resizeColumnsToContents()

    def connections(self):
        self.ui.btnOpen.clicked.connect(self.openFileNamesDialog)
        self.ui.btnRun.clicked.connect(self.core.run)
        self.ui.btnWrite.clicked.connect(self.core.write_analysis)
        self.ui.btnStop.clicked.connect(self.core.stop)
        self.ui.btnQuit.clicked.connect(self.close_application)

    def set_palette(self):
        self.brush1 = QtGui.QBrush(QtGui.QColor('#F7F8F9'))  # rest
        self.brush1.setStyle(QtCore.Qt.SolidPattern)
        self.brush2 = QtGui.QBrush(QtGui.QColor('#F7BF65'))  # last hour
        self.brush2.setStyle(QtCore.Qt.SolidPattern)
        self.brush3 = QtGui.QBrush(QtGui.QColor('#FF6B68'))  # last 10 min
        self.brush3.setStyle(QtCore.Qt.SolidPattern)

        self.brush4 = QtGui.QBrush(QtGui.QColor('#C6EBBE'))  # last 10 min
        self.brush4.setStyle(QtCore.Qt.SolidPattern)
        self.brush5 = QtGui.QBrush(QtGui.QColor('#A9DBB8'))  # last 10 min
        self.brush5.setStyle(QtCore.Qt.SolidPattern)
        self.brush6 = QtGui.QBrush(QtGui.QColor('#7CA5B8'))  # last 10 min
        self.brush6.setStyle(QtCore.Qt.SolidPattern)
        self.brush7 = QtGui.QBrush(QtGui.QColor('#FAF8D4'))  # last 10 min
        self.brush7.setStyle(QtCore.Qt.SolidPattern)
        self.brush8 = QtGui.QBrush(QtGui.QColor('#7CA5B8'))  # last 10 min
        self.brush8.setStyle(QtCore.Qt.SolidPattern)

    def update_tableFlights(self, op_list):
        op_list.sort(reverse=True)
        self.ui.tableFlights.clearContents()
        epoch_now = self.core.dataExtractor.extract_data.epoch_now
        for m, op in enumerate(op_list):
            # self.tableWidget.setRowCount(m)
            for n, item in enumerate(op.get_op_rows()):
                newItem = QtWidgets.QTableWidgetItem(item)
                if epoch_now - op.op_timestamp < 900:  # TODO coloring based on current time and not latest op
                    newItem.setBackground(self.brush3)
                elif epoch_now - op.op_timestamp < 3600:
                    newItem.setBackground(self.brush2)

                self.ui.tableFlights.setItem(m, n, newItem)
        self.ui.tableFlights.resizeColumnsToContents()

    def update_tableConfig(self, config_list):
        self.ui.tableConfig.clearContents()
        for m, config in enumerate(config_list):
            for n, item in enumerate(config.listed()):
                newItem = QtWidgets.QTableWidgetItem(item)
                if n < 3 or n > 12:
                    newItem.setBackground(self.brush7)
                elif 2 < n < 5:
                    newItem.setBackground(self.brush6)
                elif 4 < n < 9:
                    newItem.setBackground(self.brush4)
                elif 8 < n < 13:
                    newItem.setBackground(self.brush5)

                self.ui.tableConfig.setItem(m, n, newItem)
        self.ui.tableConfig.resizeColumnsToContents()

    def setClock(self, timeStr):
        self.ui.lblTime.setText(timeStr)

    def setCurrent(self, string):
        self.ui.lblCurrent.setText(string)

    def setHap(self, string):
        self.ui.lblHap.setText(string)

    def update_progressbar(self, val):
        self.ui.progressBar.setValue(val)

    def closeEvent(self, QCloseEvent):
        QCloseEvent.ignore()
        self.close_application()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self.ui.form, 'Exit box', "Exit program?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.core.stop()
            print('Bye!')
            sys.exit()
        else:
            pass

    def openFileNamesDialog(self):
        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self.ui.form, "QFileDialog.getOpenFileNames()",
                                                          "", "All Files (*);;Hexx Files (*.hex)", options=options)
        if files:
            self.core.infiles = [file(infile) for infile in files]
            print(files)


def make_controller(ui):
    controller = Controller(ui)
    return controller
