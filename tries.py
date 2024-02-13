# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI/login_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(473, 370)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.username_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.username_line_edit.setGeometry(QtCore.QRect(90, 70, 291, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.username_line_edit.setFont(font)
        self.username_line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.username_line_edit.setObjectName("username_line_edit")
        self.password_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.password_line_edit.setGeometry(QtCore.QRect(90, 150, 291, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.password_line_edit.setFont(font)
        self.password_line_edit.setAutoFillBackground(False)
        self.password_line_edit.setInputMask("")
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.password_line_edit.setDragEnabled(False)
        self.password_line_edit.setObjectName("password_line_edit")
        self.username_label = QtWidgets.QLabel(self.centralwidget)
        self.username_label.setGeometry(QtCore.QRect(90, 40, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.username_label.setFont(font)
        self.username_label.setAlignment(QtCore.Qt.AlignCenter)
        self.username_label.setObjectName("username_label")
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setGeometry(QtCore.QRect(90, 120, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.password_label.setFont(font)
        self.password_label.setAlignment(QtCore.Qt.AlignCenter)
        self.password_label.setObjectName("password_label")
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setGeometry(QtCore.QRect(140, 220, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.login_button.setFont(font)
        self.login_button.setObjectName("login_button")
        self.register_button = QtWidgets.QPushButton(self.centralwidget)
        self.register_button.setGeometry(QtCore.QRect(160, 270, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.register_button.setFont(font)
        self.register_button.setObjectName("register_button")
        self.show_passwrd_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.show_passwrd_checkBox.setGeometry(QtCore.QRect(380, 160, 91, 18))
        self.show_passwrd_checkBox.setObjectName("show_passwrd_checkBox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.username_line_edit.setPlaceholderText(_translate("MainWindow", "Username..."))
        self.password_line_edit.setPlaceholderText(_translate("MainWindow", "Password..."))
        self.username_label.setText(_translate("MainWindow", "Username"))
        self.password_label.setText(_translate("MainWindow", "Password"))
        self.login_button.setText(_translate("MainWindow", "Login"))
        self.register_button.setText(_translate("MainWindow", "Register"))
        self.show_passwrd_checkBox.setText(_translate("MainWindow", "show password"))