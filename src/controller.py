import core
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import aircraft_model
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from p_tools import time_string
import calendar
import threading

flight_headers = ['call', 'icao', 'type', 'operator', 'opTimestamp','opTimestampDate','#pos','V(fpm)','GS(kts)','(deg)',
                  'track','runway', 'L/TO', 'change_comm','miss_comm','op_comm', 'SID/STAR']
config_headers = ['From time', 'Until time', 'Duration', 'Config', 'Total', '32L', '32R', '36L', '36R', '18L', '18R', '14L', '14R',
                  'missed', 'Slack']
comboBox_config_options = ['N&S', 'N', 'S']
comboBox_plotBin_options = ['10', '15', '30', '60', '120']


class Controller:
    def __init__(self, ui):
        self.core = core.coreClass
        self.ui = ui
        self.core.set_controller(self)
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock3 = threading.Lock()
        self.lock4 = threading.Lock()
        self.lock5 = threading.Lock()
        self.lock6 = threading.Lock()
        self.lock7 = threading.Lock()

        # set up
        self.disable_run(True)
        self.disable_stop_pause(True)

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
        self.ui.comboBox_plotBin.setCurrentIndex(1)

        # connections
        self.ui.btnOpen.clicked.connect(self.openFileNamesDialog)
        self.ui.btnRun.clicked.connect(self.core.run)
        self.ui.btnWrite.clicked.connect(self.write_analysis)
        self.ui.btnStop.clicked.connect(self.core.stop)
        self.ui.btnPause.clicked.connect(self.core.pause)
        self.ui.btnLiveRun.clicked.connect(self.core.live_run)
        self.ui.checkBox_plotOff.stateChanged.connect(self.state_plot_off)
        self.ui.comboBox_plotBin.currentIndexChanged.connect(self.handle_comboBox_binsize)
        self.ui.checkBox_scrollable.stateChanged.connect(self.state_scrollable)
        self.ui.checkBox_labels.stateChanged.connect(self.state_labels)
        self.ui.checkBox_gridOn.stateChanged.connect(self.state_grid)
        self.ui.checkBox_alt_ths.stateChanged.connect(self.state_alt_ths)
        self.ui.lineEdit_alt_ths.editingFinished.connect(self.handleAltThs)
        self.ui.lineEdit_filter_airline.editingFinished.connect(self.handle_airline_filter)
        self.ui.lineEdit_filter_model.editingFinished.connect(self.handle_model_filter)
        self.ui.dateTimeEdit_analyseStart.dateTimeChanged.connect(self.handle_analyseStart)
        self.ui.dateTimeEdit_analyseEnd.dateTimeChanged.connect(self.handle_analyseEnd)
        self.ui.dateTimeEdit_filterStart.dateTimeChanged.connect(self.handle_filterStart)
        self.ui.dateTimeEdit_filterEnd.dateTimeChanged.connect(self.handle_filterEnd)
        self.ui.comboBox_config.currentIndexChanged.connect(self.handle_comboBox_config)
        self.ui.checkBox_waypoints.stateChanged.connect(self.state_waypoints)
        self.ui.pushButton_resetFilter.clicked.connect(self.reset_filters)
        self.ui.checkBoxDelimit.stateChanged.connect(self.delimited_analysis)
        self.ui.spinBoxRate.valueChanged.connect(self.handle_refreshRate)
        self.ui.lineEdit_outName.editingFinished.connect(self.handle_out_filename)

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
        self.core.stop()
        sys.exit()  # TODO without this line there will be a pop-up to close the application
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
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self.ui.form, "QFileDialog.getOpenFileNames()",
                                                          "", "All Files (*);;Hexx Files (*.hex)", options=options)
        if files:
            self.core.infiles = [file(infile) for infile in files]
            self.disable_run(False)
            print(files)
        self.setCurrent('%d files selected' % (len(files)))

    def update_tableFlights(self, op_list, epoch_now):
        op_list.sort(reverse=True)
        self.ui.tableFlights.clearContents()
        for m, op in enumerate(op_list):
            if m == self.ui.tableFlights.rowCount():
                self.ui.tableFlights.setRowCount(m+1)
            for n, item in enumerate(op.get_op_rows()):
                newItem = QtWidgets.QTableWidgetItem(item)
                color = None

                if epoch_now - op.get_op_timestamp() < 900:
                    color = self.color3
                elif epoch_now - op.get_op_timestamp() < 3600:
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
        config_list.sort()
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

    def disable_run(self, bool):
        with self.lock5:
            self.ui.btnRun.setDisabled(bool)
            self.ui.btnLiveRun.setDisabled(bool)

    def disable_stop_pause(self, bool):
        with self.lock7:
            self.ui.btnPause.setDisabled(bool)
            self.ui.btnStop.setDisabled(bool)

    def setClock(self, timeStr):
        with self.lock6:
            self.ui.lblTime.setText(timeStr)

    def setCurrent(self, string):
        with self.lock3:
            self.ui.lblCurrent.setText(string)
        self.print_console("current file label changed: " + string)

    def setHap(self, string):
        with self.lock2:
            self.ui.lblHap.setText(string)
        self.print_console("process state label changed: " + string)

    def update_progressbar(self, val):
        with self.lock4:
            self.ui.progressBar.setValue(val)

    def delimited_analysis(self, checked):
        self.core.is_delimited = bool(checked)
        self.print_console('delimited analysis: ' + str(bool(checked)))

    def update_histo(self, op_list, config_list):
        try:
            self.histo.update_figure(op_list, config_list)
        except:
            self.print_console("[!] Error with plotting histogram...")

    def state_stacked(self, checked):
        self.ui.matplotlibWidget.stacked = bool(checked)
        self.print_console('stacked: ' + str(bool(checked)))

    def state_scrollable(self, checked):
        self.ui.matplotlibWidget.scroll_resize = bool(checked)
        self.print_console('scroll resize: ' + str(bool(checked)))

    def state_grid(self, checked):
        self.ui.matplotlibWidget.grid_on = bool(checked)
        self.print_console('grid on: ' + str(bool(checked)))

    def state_labels(self, checked):
        self.ui.matplotlibWidget.show_labels = bool(checked)
        self.print_console('labels on: ' + str(bool(checked)))

    def state_alt_ths(self, checked):
        aircraft_model.Operation.use_alt_ths_timestamp = bool(checked)
        self.print_console('alt ths timestamp: ' + str(bool(checked)))

    def state_plot_off(self, checked):
        self.ui.matplotlibWidget.plot_off = bool(checked)
        self.print_console('plot off: ' + str(bool(checked)))

    def state_waypoints(self, checked):
        self.core.evaluate_waypoints = bool(checked)
        self.print_console('evaluate waypoints: ' + str(bool(checked)))

    def print_console(self, new_text):
        with self.lock1:
            self.core.console_text += new_text + '\n'
            self.ui.console.setPlainText(self.core.console_text)

    def write_analysis(self):
        self.core.write_analysis(True)

    def handleAltThs(self):
        if self.ui.lineEdit_alt_ths.isModified():
            new_alt_ths = self.ui.lineEdit_alt_ths.text()
            try:
                aircraft_model.Operation.alt_threshold = int(new_alt_ths)*0.3048  # input is in feet
                self.print_console("new altitude threshold for timestamp: " + str(new_alt_ths) + " feet")
            except Exception:
                self.print_console("[error] new altitude threshold for timestamp: only integers please")
        self.ui.lineEdit_alt_ths.setModified(False)

    def handle_out_filename(self):
        if self.ui.lineEdit_outName.isModified():
            self.core.out_name = self.ui.lineEdit_outName.text()
            self.print_console("out file name set to: " + self.ui.lineEdit_outName.text())
        self.ui.lineEdit_outName.setModified(False)

    def handle_airline_filter(self):
        if self.ui.lineEdit_filter_airline.isModified():
            airline_filter_list = [s.strip().upper() for s in self.ui.lineEdit_filter_airline.text().split(',')]
            self.core.airline_filter = airline_filter_list if airline_filter_list[0] else None
            self.core.make_display()
            self.print_console("new airline filter set to: " + ', '.join(airline_filter_list))
        self.ui.lineEdit_filter_airline.setModified(False)

    def handle_model_filter(self):
        if self.ui.lineEdit_filter_model.isModified():
            model_filter_list = [s.strip().upper() for s in self.ui.lineEdit_filter_model.text().split(',')]
            self.core.model_filter = model_filter_list if model_filter_list[0] else None
            self.core.make_display()
            self.print_console("new model filter set to: " + ', '.join(model_filter_list))
        self.ui.lineEdit_filter_model.setModified(False)

    def handle_analyseStart(self):
        self.core.analyseStart = calendar.timegm(self.ui.dateTimeEdit_analyseStart.dateTime().toPyDateTime().timetuple())
        self.print_console("new analyse start set to: " + str(self.ui.dateTimeEdit_analyseStart.dateTime().toPyDateTime()))

    def handle_analyseEnd(self):
        self.core.analyseEnd = calendar.timegm(self.ui.dateTimeEdit_analyseEnd.dateTime().toPyDateTime().timetuple())
        self.print_console("new analyse end set to: " + str(self.ui.dateTimeEdit_analyseEnd.dateTime().toPyDateTime()))

    def handle_filterStart(self):
        self.core.start_filter = calendar.timegm(self.ui.dateTimeEdit_filterStart.dateTime().toPyDateTime().timetuple())
        self.core.make_display()
        self.print_console("new filter start set to: " + str(self.ui.dateTimeEdit_filterStart.dateTime().toPyDateTime()))

    def handle_filterEnd(self):
        self.core.end_filter = calendar.timegm(self.ui.dateTimeEdit_filterEnd.dateTime().toPyDateTime().timetuple())
        self.core.make_display()
        self.print_console("new filter end set to: " + str(self.ui.dateTimeEdit_filterEnd.dateTime().toPyDateTime()))

    def handle_comboBox_config(self):
        self.core.config_filter = comboBox_config_options[self.ui.comboBox_config.currentIndex()]
        self.core.make_display()
        self.print_console("config filter set to: " + comboBox_config_options[self.ui.comboBox_config.currentIndex()])

    def handle_comboBox_binsize(self):
        self.ui.matplotlibWidget.binsize = int(comboBox_plotBin_options[self.ui.comboBox_plotBin.currentIndex()]) * 60
        self.core.make_display()
        self.print_console("histogram bin size set to: " + comboBox_plotBin_options[self.ui.comboBox_plotBin.currentIndex()] + " min")

    def reset_filters(self):
        self.core.airline_filter = None
        self.core.model_filter = None
        self.core.config_filter = None
        self.core.start_filter = None
        self.core.end_filter = None
        self.core.make_display()
        self.print_console("reset filters and display")

    def handle_refreshRate(self):
        self.core.refreshRate = int(self.ui.spinBoxRate.value())
        self.print_console("refresh rate for live run set to: " + str(self.ui.spinBoxRate.value()) + " seconds")


class MatplotlibWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        self.figure = Figure(edgecolor='k')
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15)
        self.figure.set_size_inches(7, 3)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title('Dep/Arr')

        self.scroll = QtWidgets.QScrollArea(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scroll.sizePolicy().hasHeightForWidth())
        self.scroll.setSizePolicy(sizePolicy)
        self.scroll.setWidget(self.canvas)

        self.layoutVertical = QtWidgets.QVBoxLayout(self)
        self.layoutVertical.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layoutVertical.setContentsMargins(0, 0, 0, 0)
        self.nav = NavigationToolbar(self.canvas, self)

        self.prop = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prop.sizePolicy().hasHeightForWidth())
        self.prop.setSizePolicy(sizePolicy)

        self.layoutVertical.addWidget(self.nav)
        self.layoutVertical.addWidget(self.prop)
        self.layoutVertical.addWidget(self.scroll)

        # self.scroll.resize(self.layoutVertical.geometry().width(), self.layoutVertical.geometry().height())

        self.bins = [1]
        self.binsize = 15*60  # min
        self.max_y = 0
        self.plot_off = False
        self.scroll_resize = False
        self.show_labels = False
        self.grid_on = True
        self.reset_fig()
        self.first_timestamp = None

    def reset_fig(self):
        self.axes.clear()
        self.axes.set_title('Dep/Arr', loc='center')
        self.axes.grid(self.grid_on)
        self.axes.set_xticklabels([''])
        self.resize_fig()

    def resize_fig(self):
        if not self.plot_off:
            dpi1 = self.figure.get_dpi()
            if self.scroll_resize and len(self.bins) >= 5 and len(self.bins)*50 >= self.scroll.width():
                self.figure.set_size_inches(len(self.bins)*50 / float(dpi1),
                                            (self.scroll.height()-20) / float(dpi1))
                self.canvas.resize(self.figure.get_figwidth() * float(dpi1), self.figure.get_figheight() * float(dpi1))
            else:
                self.figure.set_size_inches((self.scroll.width()) / float(dpi1),
                                            (self.scroll.height()-20) / float(dpi1))
                self.canvas.resize(self.figure.get_figwidth()*float(dpi1), self.figure.get_figheight()*float(dpi1))

    def update_figure(self, op_list, config_list):
        if not self.plot_off and op_list:
            self.reset_fig()
            dep = [0]
            arr = [0]
            labels = []

            if not self.first_timestamp: self.first_timestamp = op_list[-1].get_op_timestamp()

            for op in reversed(op_list):
                index = int((op.get_op_timestamp() - self.first_timestamp) / self.binsize)
                # fill in labels and empty values for new bars
                if index >= len(labels):
                    for m in reversed(range(index - len(labels) + 1)):
                        bin_time = op.get_op_timestamp() - m*self.binsize
                        labels.append(time_string(bin_time - (bin_time % self.binsize)))
                    dep.extend([0] * (index - len(dep) + 1))
                    arr.extend([0] * (index - len(arr) + 1))

                if op.LorT == 'T':
                    dep[index] += 1
                elif op.LorT == 'L':
                    arr[index] += 1

            N = len(labels)
            self.bins = np.arange(N)
            width = 0.8
            # plot stacked bars
            p1 = self.axes.bar(self.bins, arr, width, color='#9CB380')
            p2 = self.axes.bar(self.bins, dep, width, bottom=arr, color='#5CC8FF')
            # set legend and labels (not always so they don't overlap)
            self.axes.legend((p2[0], p1[0]), ('Dep', 'Arr'), loc=0)
            self.axes.set_xticks(self.bins - 0.5)
            if len(labels) > 10:
                i = 0
                one_label_per = len(labels) / 15
                for m, label in enumerate(labels):
                    if i > 0:
                        labels[m] = ''
                    i += 1
                    if i > one_label_per: i = 0
            self.axes.set_xticklabels(labels, rotation=-40)
            self.max_y = self.axes.get_ylim()[1]
            self.axes.set_xlim(-1, N)
            x_offset = 0.2
            # set text for count of each bar
            if self.show_labels:
                for m, label in enumerate(labels):
                    if arr[m] != 0:
                        self.axes.text(self.bins[m] - x_offset,
                                       arr[m] + self.max_y*0.01, '{:.0f}'.format(arr[m]))
                    if dep[m] != 0:
                        self.axes.text(self.bins[m] + x_offset/2,
                                       dep[m] + arr[m] + self.max_y*0.01, '{:.0f}'.format(dep[m]))
            # config change vertical lines and text
            for m, config in enumerate(config_list):
                x = float((config.from_epoch - self.first_timestamp) / self.binsize)
                self.axes.plot([x]*2, [0, 0.9*self.max_y], 'b--', linewidth=1)
                self.axes.text(x + x_offset, self.max_y*0.9, config.config, fontsize=16)
            # show plot
            self.canvas.draw()


def make_controller(ui):
    controller = Controller(ui)
    return controller
