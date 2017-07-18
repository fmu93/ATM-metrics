import core
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import aircraft_model
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from matplotlib.pyplot import xticks
from p_tools import time_string
import time

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
        self.ui.btnWrite.clicked.connect(self.core.write_analysis)
        self.ui.btnStop.clicked.connect(self.core.stop)
        self.ui.btnPause.clicked.connect(self.core.pause)
        self.ui.btnLightRun.clicked.connect(self.core.light_run)
        self.ui.checkBox_plotOff.stateChanged.connect(self.state_plot_off)
        # self.ui.checkBox_stacked.stateChanged.connect(self.state_stacked)
        # self.ui.checkBox_scrollable.stateChanged.connect(self.state_scrollable)  # TODO reenable
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
        self.ui.checkBox_liveRun.stateChanged.connect(self.state_live_run)
        # self.ui.pushButton_resetFilter.clicked.connect(self.reset_filters)
        # self.ui.checkBoxDelimit.stateChanged.connect(self.delimited_analysis)



        # TODO state delimited timedate analysis


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
        sys.exit()  # TODO delete this lines
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
            self.disable_run(False)
            print(files)
        self.setCurrent('%d files selected' % (len(files)))

    def update_tableFlights(self, op_list, epoch_now):
        op_list.sort(reverse=True)
        self.ui.tableFlights.clearContents()
        for m, op in enumerate(op_list):
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
        self.ui.btnRun.setDisabled(bool)
        self.ui.btnLightRun.setDisabled(bool)

    def disable_for_light(self, bool):
        self.ui.tabWidget.setDisabled(bool)

    def setClock(self, timeStr):
        self.ui.lblTime.setText(timeStr)

    def setCurrent(self, string):
        self.ui.lblCurrent.setText(string)
        self.print_console("current file label changed: " + string)

    def setHap(self, string):
        self.ui.lblHap.setText(string)
        self.print_console("process state label changed: " + string)

    def update_progressbar(self, val):
        self.ui.progressBar.setValue(val)  # TODO run gui only from main thread
        # if isinstance(threading.current_thread(), threading._MainThread):
        #     self.ui.progressBar.setValue(val)
        # else:
        #     self.core.q.put((self.update_progressbar, (val,), {}))  # send the answer to the main thread's queue

    def delimited_analysis(self, checked):
        self.core.is_delimited = bool(checked)
        self.print_console('delimited analysis: ' + str(bool(checked)))

    def update_histo(self):
        self.histo.update_figure()

    def state_stacked(self, checked):
        self.ui.matplotlibWidget.stacked = bool(checked)
        self.print_console('stacked: ' + str(bool(checked)))

    def state_scrollable(self, checked):
        self.ui.matplotlibWidget.scroll_resize = bool(checked)
        self.print_console('scroll resize: ' + str(bool(checked)))

    def state_grid(self, checked):
        self.ui.matplotlibWidget.set_grid(bool(checked))
        self.print_console('grid on: ' + str(bool(checked)))

    def state_labels(self, checked):
        self.ui.matplotlibWidget.show_labels = bool(checked)
        self.print_console('labels on: ' + str(bool(checked)))

    def state_alt_ths(self, checked):
        aircraft_model.use_alt_ths_timestamp = bool(checked)
        self.print_console('alt ths timestamp: ' + str(bool(checked)))

    def state_plot_off(self, checked):
        self.ui.matplotlibWidget.plot_off = bool(checked)
        self.print_console('plot off: ' + str(bool(checked)))

    def state_waypoints(self, checked):
        self.core.evaluate_waypoints = bool(checked)
        self.print_console('evaluate waypoints: ' + str(bool(checked)))

    def state_live_run(self, checked):
        self.core.live_run = bool(checked)
        self.print_console('is live run: ' + str(bool(checked)))

    def print_console(self, new_text):
        self.core.console_text += new_text + '\n'
        self.ui.console.setPlainText(self.core.console_text)

    def handleAltThs(self):
        if self.ui.lineEdit_alt_ths.isModified():
            new_alt_ths = self.ui.lineEdit_alt_ths.text()
            try:
                aircraft_model.alt_threshold = int(new_alt_ths)*0.3048  # input is in feet
                self.print_console("new altitude threshold for timestamp: " + str(new_alt_ths) + " feet")
            except Exception:
                self.print_console("[error] new altitude threshold for timestamp: only integers please")
        self.ui.lineEdit_alt_ths.setModified(False)

    def handle_airline_filter(self):
        if self.ui.lineEdit_filter_airline.isModified():
            airline_filter_list = self.ui.lineEdit_filter_airline.text().strip(' ').upper().split(',')
            self.core.airline_filter = airline_filter_list if airline_filter_list[0] else None
            self.core.make_display()
            self.print_console("new airline filter set to: " + ','.join(airline_filter_list))
        self.ui.lineEdit_filter_airline.setModified(False)

    def handle_model_filter(self):
        if self.ui.lineEdit_filter_model.isModified():
            model_filter_list = self.ui.lineEdit_filter_model.text().strip(' ').upper().split(',')
            self.core.model_filter = model_filter_list if model_filter_list[0] else None
            self.core.make_display()
            self.print_console("new model filter set to: " + ','.join(model_filter_list))
        self.ui.lineEdit_filter_model.setModified(False)

    def handle_analyseStart(self):
        self.core.analyseStart = time.mktime(self.ui.dateTimeEdit_analyseStart.dateTime().toPyDateTime().timetuple())
        self.print_console("new analyse start set to: " + str(self.ui.dateTimeEdit_analyseStart.dateTime().toPyDateTime()))

    def handle_analyseEnd(self):
        self.core.analyseEnd = time.mktime(self.ui.dateTimeEdit_analyseEnd.dateTime().toPyDateTime().timetuple())
        self.print_console("new analyse end set to: " + str(self.ui.dateTimeEdit_analyseEnd.dateTime().toPyDateTime()))

    def handle_filterStart(self):
        self.core.start_filter = time.mktime(self.ui.dateTimeEdit_filterStart.dateTime().toPyDateTime().timetuple())
        self.core.make_display()
        self.print_console("new filter start set to: " + str(self.ui.dateTimeEdit_filterStart.dateTime().toPyDateTime()))

    def handle_filterEnd(self):
        self.core.end_filter = time.mktime(self.ui.dateTimeEdit_filterEnd.dateTime().toPyDateTime().timetuple())
        self.core.make_display()
        self.print_console("new filter end set to: " + str(self.ui.dateTimeEdit_filterEnd.dateTime().toPyDateTime()))

    def handle_comboBox_config(self):
        self.core.config_filter = comboBox_config_options[self.ui.comboBox_config.currentIndex()]
        self.core.make_display()
        self.core.make_display()
        self.print_console("config filter set to: " + comboBox_config_options[self.ui.comboBox_config.currentIndex()])

    def reset_filters(self):
        self.core.airline_filter = None
        self.core.model_filter = None
        self.core.config_filter = None
        self.core.start_filter = None
        self.core.end_filter = None
        self.core.make_display()


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
        self.max_y = self.binsize*1.2
        self.plot_off = True
        self.scroll_resize = False
        self.show_labels = False
        self.reset_fig()
        self.axes.grid(True)

    def set_grid(self, bool):
        self.axes.grid(bool)

    def reset_fig(self):
        self.axes.clear()
        self.axes.set_title('Dep/Arr', loc='center')
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

    def update_figure(self, op_list, config_list):  # TODO x axis, adaptive labels and grid
        if not self.plot_off:
            self.reset_fig()
            # operation histogram
            # last_time = op_list[0].get_op_timestamp() - op_list[0].get_op_timestamp() % (self.binsize * 60)
            dep = []
            arr = []
            for m, op in enumerate(op_list):
                if op.LorT == 'T':
                    dep.append(op.get_op_timestamp())
                elif op.LorT == 'L':
                    arr.append(op.get_op_timestamp())
            self.bins = np.arange(arr[0], arr[-1])

            [n0, n1], bins2, patches = self.axes.hist([arr, dep], bins=self.bins, stacked=True, rwidth=0.9,
                                                      color=['#9CB380', '#5CC8FF'], label=['arr', 'dep'])
            if n1.any() and max(n1) > self.max_y:
                self.max_y = max(n1)+2

            # labels is an array of tick labels.
            label_text = [time_string(loc) for loc in xticks()[0]]
            self.axes.set_xticklabels(label_text)

            self.axes.legend(loc=2)
            if self.show_labels:
                for m1, count1 in enumerate(n0):
                    self.axes.text(self.bins[m1] + self.binsize*0.25, count1+self.max_y*0.02, '{:.0f}'.format(count1))
                for m2, count2 in enumerate(n1):
                    self.axes.text(self.bins[m2] + self.binsize*0.75, count2+self.max_y*0.02, '{:.0f}'.format(count2))

            # config changes vertical lines
            for m, config in enumerate(config_list):
                self.axes.plot([config.from_epoch]*2, [0, 0.85*self.max_y], 'b--', linewidth=1)
                self.axes.text(config.from_epoch-self.binsize*0.2, self.max_y*0.9, config.config)

            # line of mean horizontal line (per day)
            avg = np.average(n1)
            self.axes.plot(self.bins, [avg] * len(self.bins), 'k--', linewidth=0.6)
            self.prop.setText("\tBin size is: " + '{:d}'.format(self.binsize) + " min\t"
                              "Average throughput per bin: " + '{:.1f}'.format(avg))

            # show plot
            self.axes.set_xticks(self.bins)
            self.axes.set_xlim([0, self.bins[-1]+self.binsize])
            self.axes.set_ylim([0, self.max_y])
            self.canvas.draw()


def make_controller(ui):
    controller = Controller(ui)
    return controller
