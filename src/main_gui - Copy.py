# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Wed Jun 21 19:33:56 2017
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from p_tools import time_string
import controller
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
        self.btnOpen = QtWidgets.QPushButton(Form)
        self.btnOpen.setObjectName("btnOpen")
        self.horizontalLayout.addWidget(self.btnOpen)
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
        self.lblTime = QtWidgets.QLabel(Form)
        self.horizontalLayout.addWidget(self.lblTime)
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
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Runway Allocation"))
        self.btnOpen.setText(_translate("Form", "Open"))
        self.btnRun.setText(_translate("Form", "Run"))
        self.btnWrite.setText(_translate("Form", "Write"))
        self.btnStop.setText(_translate("Form", "Stop"))
        self.btnQuit.setText(_translate("Form", "Quit"))
        self.lblTime.setText(_translate("dashboard", "...", None))

    def set_controller(self, controller2):
        self.controller = controller2


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
    ui.set_controller(controller.make_controller(ui))
    form.show()
    sys.exit(app.exec_())

