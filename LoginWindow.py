import socket
from PyQt5.QtGui import QFont
from RegisterWindow import Ui_RegisterWindow
from WhatsappMain import Ui_MainWhatsapp
import sys
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont, QMouseEvent
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import json

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1
USERNAME = ""
sent_to = ""

CHATS = {}


def add_to_CHATS(name):
    if name not in CHATS:
        CHATS[name] = []


class UiMainWindow(object):
    def __init__(self):
        self.main_window = None
        self.central_widget = None
        self.send = None
        self.label = None
        self.label_2 = None
        self.label_3 = None
        self.password_text = None
        self.name_text = None
        self.register_button = None
        self.menu_bar = None
        self.statusbar = None
        self.client_socket = None
        self.window = None
        self.ui = None

    def setupUi(self, main_window):
        self.main_window = main_window
        main_window.setObjectName("main_window")
        main_window.resize(319, 204)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.send = QtWidgets.QPushButton(self.central_widget)
        self.send.setGeometry(QtCore.QRect(100, 100, 111, 21))
        self.send.setObjectName("send")
        self.label = QtWidgets.QLabel(self.central_widget)
        self.label.setGeometry(QtCore.QRect(80, 30, 161, 31))
        self.label.setObjectName("label")
        self.password_text = QtWidgets.QLineEdit(self.central_widget)
        self.password_text.setGeometry(QtCore.QRect(100, 80, 111, 21))
        self.password_text.setObjectName("password_text")
        self.name_text = QtWidgets.QLineEdit(self.central_widget)
        self.name_text.setGeometry(QtCore.QRect(100, 60, 111, 21))
        self.name_text.setObjectName("name_text")
        self.label_2 = QtWidgets.QLabel(self.central_widget)
        self.label_2.setGeometry(QtCore.QRect(60, 60, 31, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.central_widget)
        self.label_3.setGeometry(QtCore.QRect(40, 80, 61, 21))
        self.label_3.setObjectName("label_3")
        self.register_button = QtWidgets.QPushButton(self.central_widget)
        self.register_button.setGeometry(QtCore.QRect(110, 120, 91, 41))
        self.register_button.setObjectName("registerButton")
        self.register_button.setText("Register")
        self.register_button.setFont(QFont('Arial', 16))
        main_window.setCentralWidget(self.central_widget)
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 319, 22))
        self.menu_bar.setObjectName("menubar")
        main_window.setMenuBar(self.menu_bar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.translate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def translate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "main_window"))
        self.send.setText(_translate("main_window", "send"))
        self.label.setText(_translate("main_window", "Enter you name and password"))
        self.label_2.setText(_translate("main_window", "name:"))
        self.label_3.setText(_translate("main_window", "password:"))

        self.send.clicked.connect(self.send_function)
        self.register_button.clicked.connect(lambda: self.register("Yes"))

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (SERVER_IP, SERVER_PORT)
        client_sock.connect(server_address)
        self.client_socket = client_sock

    def send_function(self):
        self.client_socket.sendall(f"1@@{self.name_text.text()},{self.password_text.text()}".encode())
        return_code = self.client_socket.recv(1024).decode()
        print(return_code)
        if return_code == "1":
            # run main whatsapp
            self.window = QtWidgets.QMainWindow()
            ui = Ui_MainWhatsapp()
            ui.setupUi(self.window, self.name_text.text(), self.client_socket)
            # MainWindow.show()
            self.window.show()
            self.main_window.close()

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
            self.ui.setupUi(self.window, self.client_socket)
            self.window.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()


if __name__ == "__main__":
    main()
