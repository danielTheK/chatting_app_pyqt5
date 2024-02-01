import socket
from PyQt5.QtGui import QFont
from registerWindow import Ui_RegisterWindow
from whatsapp_main import Ui_MainWhatsapp

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1
USERNAME = ""
sent_to = ""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont, QMouseEvent
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import json
CHATS = {}


def add_to_CHATS(name):
    if name not in CHATS:
        CHATS[name] = []


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(319, 204)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.send = QtWidgets.QPushButton(self.centralwidget)
        self.send.setGeometry(QtCore.QRect(100, 100, 111, 21))
        self.send.setObjectName("send")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 30, 161, 31))
        self.label.setObjectName("label")
        self.passwordText = QtWidgets.QLineEdit(self.centralwidget)
        self.passwordText.setGeometry(QtCore.QRect(100, 80, 111, 21))
        self.passwordText.setObjectName("passwordText")
        self.nameText = QtWidgets.QLineEdit(self.centralwidget)
        self.nameText.setGeometry(QtCore.QRect(100, 60, 111, 21))
        self.nameText.setObjectName("nameText")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(60, 60, 31, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 80, 61, 21))
        self.label_3.setObjectName("label_3")
        self.registerButton = QtWidgets.QPushButton(self.centralwidget)
        self.registerButton.setGeometry(QtCore.QRect(110, 120, 91, 41))
        self.registerButton.setObjectName("registerButton")
        self.registerButton.setText("Register")
        self.registerButton.setFont(QFont('Arial', 16))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 319, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.send.setText(_translate("MainWindow", "send"))
        self.label.setText(_translate("MainWindow", "Enter you name and password"))
        self.label_2.setText(_translate("MainWindow", "name:"))
        self.label_3.setText(_translate("MainWindow", "password:"))

        self.send.clicked.connect(self.sendFunction)
        self.registerButton.clicked.connect(lambda: self.register("Yes"))
        # connection socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (SERVER_IP, SERVER_PORT)
        client_sock.connect(server_address)
        self.client_sock = client_sock

    def sendFunction(self):
        self.client_sock.sendall(f"1@@{self.nameText.text()},{self.passwordText.text()}".encode())
        return_code = self.client_sock.recv(1024).decode()
        print(return_code)
        if return_code == "1":
            # run main whatsapp
            self.window = QtWidgets.QMainWindow()
            ui = Ui_MainWhatsapp()
            ui.setupUi(self.window, self.nameText.text(), self.client_sock)
            # MainWindow.show()
            self.window.show()
            self.MainWindow.close()

        else:
            msg = QMessageBox()
            msg.setWindowTitle("Username or password incorrect")
            msg.setText("The username or password are incorrect.\nDo you want to register?")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.buttonClicked.connect(self.register)
            msg.exec_()

    def register(self, i):
        try:
            i = i.text()[1::]
        except AttributeError:
            pass
        if i == "Yes":
            # run register whatsapp
            self.window = QtWidgets.QMainWindow()
            self.ui = Ui_RegisterWindow()
            self.ui.setupUi(self.window, self.client_sock)
            self.window.show()



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()
