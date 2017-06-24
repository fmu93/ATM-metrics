# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Wed Jun 21 19:33:56 2017
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import core
import sys


class Ui_Form(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(702, 509)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnRun = QtWidgets.QPushButton(Form)
        self.btnRun.setObjectName("btnRun")
        self.horizontalLayout.addWidget(self.btnRun)
        self.btnWrite = QtWidgets.QPushButton(Form)
        self.btnWrite.setObjectName("btnWrite")
        self.horizontalLayout.addWidget(self.btnWrite)
        self.btnStop = QtWidgets.QPushButton(Form)
        self.btnStop.setObjectName("btnStop")
        self.horizontalLayout.addWidget(self.btnStop)
        self.btnQuit = QtWidgets.QPushButton(Form)
        self.btnQuit.setObjectName("btnQuit")
        self.horizontalLayout.addWidget(self.btnQuit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayout_3.addWidget(self.tableWidget)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.set_palette()
        QtCore.QMetaObject.connectSlotsByName(Form)
        core.coreClass.set_ui(self)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Runway Allocation"))
        self.btnRun.setText(_translate("Form", "Run"))
        self.btnWrite.setText(_translate("Form", "Write"))
        self.btnStop.setText(_translate("Form", "Stop"))
        self.btnQuit.setText(_translate("Form", "Quit"))
        self.btnRun.clicked.connect(core.coreClass.run)
        self.btnWrite.clicked.connect(core.coreClass.write_analysis)
        self.btnStop.clicked.connect(core.coreClass.stop)
        self.btnQuit.clicked.connect(self.close_application)
        self.tableWidget.setColumnCount(13)
        self.tableWidget.setRowCount(100)

    def set_palette(self):
        self.brush1 = QtGui.QBrush(QtGui.QColor('#F7F8F9'))  # rest
        self.brush1.setStyle(QtCore.Qt.SolidPattern)
        self.brush2 = QtGui.QBrush(QtGui.QColor('#F7BF65'))  # last hour
        self.brush2.setStyle(QtCore.Qt.SolidPattern)
        self.brush3 = QtGui.QBrush(QtGui.QColor('#FF6B68'))  # last 10 min
        self.brush3.setStyle(QtCore.Qt.SolidPattern)

    def dataToTable(self, op_list):
        self.tableWidget.clearContents()
        for m, op in enumerate(op_list):
            # self.tableWidget.setRowCount(m)
            for n, item in enumerate(op.get_op_rows()):
                if op_list[0].op_timestamp - op.op_timestamp < 600:
                    brush = self.brush3
                elif op_list[0].op_timestamp - op.op_timestamp < 3600:
                    brush = self.brush2
                else:
                    brush = self.brush1
                newItem = QtWidgets.QTableWidgetItem(item)
                newItem.setBackground(brush)
                self.tableWidget.setItem(m, n, newItem)
        self.tableWidget.resizeColumnsToContents()

    def closeEvent(self, QCloseEvent):
        QCloseEvent.ignore()
        self.close_application()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, 'Exit box', "Exit program?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print('Bye!')
            core.coreClass.stop()
            sys.exit()
        else:
            pass


class Form(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

    def closeEvent(self, QCloseEvent):
        QCloseEvent.ignore()


def run():
    app = QtWidgets.QApplication(sys.argv)
    form = Form()
    ui = Ui_Form()
    ui.setupUi(form)
    form.show()
    sys.exit(app.exec_())

