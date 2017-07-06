import core
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from main_gui import MatplotlibWidget
import random

flight_headers = ['call', 'icao', 'type', 'operator', 'opTimestamp','opTimestampDate','#pos','V(fpm)','GS(kts)','(deg)',
              'track','runway', 'L/T', 'change_comm','miss_comm','op_comm', 'waypoints']
config_headers = ['From time', 'Until time', 'Duration', 'Config', 'Total', '32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R',
                  'missed', 'Slack (min)']
comboBox_config_options = ['N&S', 'N', 'S']
comboBox_plotBin_options = ['10', '15', '30', '60', '120']


class Controller:
    def __init__(self, ui):
        self.core = core.coreClass
        self.ui = ui
        self.core.set_controller(self)

        # table
        self.ui.tableFlights.setColumnCount(17)
        self.ui.tableFlights.setRowCount(self.core.operations_table_rows)
        self.ui.tableFlights.setHorizontalHeaderLabels(flight_headers)
        self.ui.tableFlights.resizeColumnsToContents()
        self.ui.tableConfig.setColumnCount(15)
        self.ui.tableConfig.setHorizontalHeaderLabels(config_headers)
        self.ui.tableConfig.resizeColumnsToContents()

        # comboboxes
        for t in comboBox_config_options:
            self.ui.comboBox_config.addItem(t)
        for t in comboBox_plotBin_options:
            self.ui.comboBox_plotBin.addItem(t)

        # connections
        self.ui.btnOpen.clicked.connect(self.openFileNamesDialog)
        self.ui.btnRun.clicked.connect(self.core.run)
        self.ui.btnWrite.clicked.connect(self.core.write_analysis)
        self.ui.btnStop.clicked.connect(self.core.stop)
        self.ui.btnPause.clicked.connect(self.core.pause)
        self.ui.checkBox_stacked.stateChanged.connect(self.state_stacked)
        self.ui.checkBox_scrollable.stateChanged.connect(self.state_scrollable)
        self.ui.checkBox_labels.stateChanged.connect(self.state_labels)
        # self.ui.checkBox_gridOn.stateChanged.connect(self.state_grid)


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
        # sys.exit()  # TODO delete this line
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
        self.setCurrent('%d files selected' % (len(files)))

    def update_tableFlights(self, op_list, epoch_now):
        self.ui.tableFlights.clearContents()
        for m, op in enumerate(op_list):
            for n, item in enumerate(op.get_op_rows()):
                newItem = QtWidgets.QTableWidgetItem(item)
                color = None
                if epoch_now - op.op_timestamp < 900:
                    color = self.color3
                elif epoch_now - op.op_timestamp < 3600:
                    color = self.color2

                if color:
                    if m % 2:
                        color = color.darker(107)
                    brush = QtGui.QBrush(color)
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    newItem.setBackground(brush)

                self.ui.tableFlights.setItem(m, n, newItem)
        self.ui.tableFlights.resizeColumnsToContents()

    def update_tableConfig(self, config_list):
        self.ui.tableConfig.clearContents()
        for m, config in enumerate(config_list):
            if m == self.ui.tableConfig.rowCount():
                self.ui.tableConfig.setRowCount(m+1)
            for n, item in enumerate(config.listed()):
                newItem = QtWidgets.QTableWidgetItem(item)
                color = None
                if n < 3 or n > 12:
                    color = self.color7
                elif 2 < n < 5:
                    color = self.color6
                elif 4 < n < 9:
                    color = self.color4
                elif 8 < n < 13:
                    color = self.color5

                if color:
                    if m % 2:
                        color = color.darker(107)
                    brush = QtGui.QBrush(color)
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    newItem.setBackground(brush)

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

    def update_histo(self):
        self.histo.update_figure()

    def state_stacked(self, checked):
        self.ui.matplotlibWidget.stacked = checked

    def state_scrollable(self, checked):
        self.ui.matplotlibWidget.scroll_resize = checked

    def state_grid(self, checked):
        self.ui.matplotlibWidget.gridOn = checked

    def state_labels(self, checked):
        self.ui.matplotlibWidget.show_labels = checked


def make_controller(ui):
    controller = Controller(ui)
    return controller
