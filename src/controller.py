import core
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from main_gui import MatplotlibWidget
import random

flight_headers = ['call', 'icao', 'type', 'opTimestamp','opTimestampDate','pos_count','V(fpm)','GS(kts)','(deg)',
              'track','runway','change_comm','miss_comm','op_comm', 'waypoints']
config_headers = ['From time', 'Until time', 'Dur (h)', 'Config', 'Total', '32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R',
                  'missed', 'Slack (min)']


class Controller:
    def __init__(self, ui):
        self.core = core.coreClass
        self.ui = ui
        self.core.set_controller(self)
        self.threadSample = ThreadSample(self, self.ui.Configuration)

        # table
        self.ui.tableFlights.setColumnCount(15)
        self.ui.tableFlights.setRowCount(200)
        self.ui.tableFlights.setHorizontalHeaderLabels(flight_headers)
        self.ui.tableFlights.resizeColumnsToContents()
        self.ui.tableConfig.setColumnCount(15)
        self.ui.tableConfig.setHorizontalHeaderLabels(config_headers)
        self.ui.tableConfig.resizeColumnsToContents()

        # connections
        self.ui.btnOpen.clicked.connect(self.openFileNamesDialog)
        self.ui.btnRun.clicked.connect(self.core.run)
        self.ui.btnWrite.clicked.connect(self.core.write_analysis)
        self.ui.btnStop.clicked.connect(self.core.stop)
        self.ui.btnQuit.clicked.connect(self.close_application)

        # pallete
        self.color1 = QtGui.QColor('#F7F8F9')  # rest
        self.color2 = QtGui.QColor('#F7BF65')  # orange
        self.color3 = QtGui.QColor('#FF6B68')  # light red

        self.color4 = QtGui.QColor('#C6EBBE')  # light green
        self.color5 = QtGui.QColor('#A9DBB8')  # light green 2
        self.color6 = QtGui.QColor('#7CA5B8')  # blue
        self.color7 = QtGui.QColor('#FAF8D4')  #
        self.color8 = QtGui.QColor('#7CA5B8')  # blue 2

        # plot
        self.histo = self.ui.matplotlibWidget

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
        self.threadSample.setCurrent('%d files selected' % (len(files)))


class ThreadSample(QtCore.QThread):
    def __init__(self, controller, parent=None):
        super(ThreadSample, self).__init__(parent)
        self.controller = controller

    @QtCore.pyqtSlot()
    def update_tableFlights(self, op_list):
        op_list.sort(reverse=True)
        self.controller.ui.tableFlights.clearContents()
        epoch_now = self.controller.core.dataExtractor.extract_data.epoch_now
        for m, op in enumerate(op_list):
            for n, item in enumerate(op.get_op_rows()):
                newItem = QtWidgets.QTableWidgetItem(item)
                color = None
                if epoch_now - op.op_timestamp < 900:
                    color = self.controller.color3
                elif epoch_now - op.op_timestamp < 3600:
                    color = self.controller.color2

                if color:
                    if m % 2:
                        color = color.darker(107)
                    brush = QtGui.QBrush(color)
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    newItem.setBackground(brush)

                self.controller.ui.tableFlights.setItem(m, n, newItem)
        self.controller.ui.tableFlights.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def update_tableConfig(self, config_list):
        self.controller.ui.tableConfig.clearContents()
        for m, config in enumerate(config_list):
            if m == self.controller.ui.tableConfig.rowCount():
                self.controller.ui.tableConfig.setRowCount(m+1)
            for n, item in enumerate(config.listed()):
                newItem = QtWidgets.QTableWidgetItem(item)
                color = None
                if n < 3 or n > 12:
                    color = self.controller.color7
                elif 2 < n < 5:
                    color = self.controller.color6
                elif 4 < n < 9:
                    color = self.controller.color4
                elif 8 < n < 13:
                    color = self.controller.color5

                if color:
                    if m % 2:
                        color = color.darker(107)
                    brush = QtGui.QBrush(color)
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    newItem.setBackground(brush)

                self.controller.ui.tableConfig.setItem(m, n, newItem)
        self.controller.ui.tableConfig.resizeColumnsToContents()

    @QtCore.pyqtSlot(str)
    def setClock(self, timeStr):
        self.controller.ui.lblTime.setText(timeStr)

    @QtCore.pyqtSlot()
    def setCurrent(self, string):
        self.controller.ui.lblCurrent.setText(string)

    @QtCore.pyqtSlot()
    def setHap(self, string):
        self.controller.ui.lblHap.setText(string)

    @QtCore.pyqtSlot(float)
    def update_progressbar(self, val):
        self.controller.ui.progressBar.setValue(val)

    @QtCore.pyqtSlot()
    def update_histo(self):
        self.controller.histo.update_figure()


def make_controller(ui):
    controller = Controller(ui)
    return controller
