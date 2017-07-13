import core
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import aircraft_model
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import threading

flight_headers = ['call', 'icao', 'type', 'operator', 'opTimestamp','opTimestampDate','#pos','V(fpm)','GS(kts)','(deg)',
                  'track','runway', 'L/TO', 'change_comm','miss_comm','op_comm', 'waypoints']
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
        self.ui.comboBox_plotBin.setCurrentIndex(1)

        # connections
        self.ui.btnOpen.clicked.connect(self.openFileNamesDialog)
        self.ui.btnRun.clicked.connect(self.core.run)
        self.ui.btnWrite.clicked.connect(self.core.write_analysis)
        self.ui.btnStop.clicked.connect(self.core.stop)
        self.ui.btnPause.clicked.connect(self.core.pause)
        self.ui.btnLightRun.clicked.connect(self.core.light_run)
        self.ui.checkBox_plotOff.stateChanged.connect(self.state_plot_off)
        self.ui.checkBox_stacked.stateChanged.connect(self.state_stacked)
        self.ui.checkBox_scrollable.stateChanged.connect(self.state_scrollable)
        self.ui.checkBox_labels.stateChanged.connect(self.state_labels)
        self.ui.checkBox_gridOn.stateChanged.connect(self.state_grid)
        self.ui.checkBox_alt_ths.stateChanged.connect(self.state_alt_ths)
        self.ui.lineEdit_alt_ths.editingFinished.connect(self.handleAltThs)


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
            print(files)
        self.setCurrent('%d files selected' % (len(files)))

    def update_tableFlights(self, op_list, epoch_now):
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

    def update_histo(self):
        self.histo.update_figure()

    def state_stacked(self, checked):
        self.ui.matplotlibWidget.stacked = bool(checked)
        self.print_console('stacked: ' + str(bool(checked)))

    def state_scrollable(self, checked):
        self.ui.matplotlibWidget.scroll_resize = bool(checked)
        self.print_console('scroll resize: ' + str(bool(checked)))

    def state_grid(self, checked):
        self.ui.matplotlibWidget.gridOn = bool(checked)
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
        self.binsize = 15  # min
        self.max_y = self.binsize*1.2
        self.plot_off = False
        self.scroll_resize = False
        self.show_labels = False
        self.stacked = True
        self.gridOn = True
        self.reset_fig()

    def reset_fig(self):
        self.axes.clear()
        self.axes.grid(self.gridOn)
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
            last_time = op_list[0].get_op_timestamp() - op_list[0].get_op_timestamp() % (self.binsize * 60)
            dep = []
            arr = []
            for m, op in enumerate(op_list):
                delay = (last_time - op.get_op_timestamp())/60.0
                if op.LorT == 'T':
                    dep.append(delay)
                elif op.LorT == 'L':
                    arr.append(delay)
            self.bins = np.arange(0, arr[-1]/self.binsize + 1)*self.binsize
            if self.stacked:
                [n0, n1], bins2, patches = self.axes.hist([arr, dep], bins=self.bins, stacked=True, rwidth=0.9,
                                                          color=['#9CB380', '#5CC8FF'], label=['arr', 'dep'])
                if n1.any() and max(n1) > self.max_y:
                    self.max_y = max(n1)+2
            else:  # TODO adapt all to stacked or not
                [n0, n1], bins2, patches = self.axes.hist([arr, dep], bins=self.bins, histtype='bar', rwidth=0.9,
                                                          color=['#9CB380', '#5CC8FF'], label=['arr', 'dep'])

            # n0, bins2, patches = self.axes.hist(arr, bins=self.bins, stacked=True, color='#9CB380', rwidth=0.9, label='arr')
            # n1, bins2, patches = self.axes.hist(dep, bins=self.bins, stacked=True, color='#5CC8FF', rwidth=0.9, label='dep')
            self.axes.legend(loc=2)
            # self.max_y = max([x+y for x, y in zip(n[0], n[1])])
            if self.show_labels:
                for m1, count1 in enumerate(n0):
                    self.axes.text(self.bins[m1] + self.binsize*0.25, count1+self.max_y*0.02, '{:.0f}'.format(count1))
                for m2, count2 in enumerate(n1):
                    self.axes.text(self.bins[m2] + self.binsize*0.75, count2+self.max_y*0.02, '{:.0f}'.format(count2))

            # config changes vertical lines
            for m, config in enumerate(config_list):
                self.axes.plot([(last_time - config.from_epoch)/60.0]*2, [0, 0.85*self.max_y], 'b--', linewidth=1)
                self.axes.text((last_time - config.from_epoch)/60.0-self.binsize*0.2, self.max_y*0.9, config.config)

            # line of mean horizontal line (per day)
            avg = np.average(n1)
            # avg = np.average([x+y for x, y in zip(n0, n1)])
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
