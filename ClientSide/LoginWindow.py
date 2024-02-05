import socket

from PyQt5.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont
from RegisterWindow import Ui_RegisterWindow
from WhatsappMain import Ui_MainWhatsapp
import sys
from PyQt5.QtWidgets import QMessageBox, QPushButton, QStatusBar, QLineEdit, QLabel, QWidget
from PyQt5.QtGui import QFont, QMouseEvent
import threading
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8865
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
        self.username_label = None
        self.password_label = None
        self.username_line_edit = None
        self.password_line_edit = None
        self.login_button = None
        self.register_button = None
        self.menu_bar = None
        self.statusbar = None
        self.client_socket = None
        self.window = None
        self.ui = None

    def setupUi(self, main_window):
        if not main_window.objectName():
            main_window.setObjectName(u"main_window")
        main_window.resize(473, 370)
        self.central_widget = QWidget(main_window)
        self.central_widget.setObjectName(u"central_widget")
        self.username_line_edit = QLineEdit(self.central_widget)
        self.username_line_edit.setObjectName(u"username_line_edit")
        self.username_line_edit.setGeometry(QRect(90, 70, 291, 31))
        font = QFont()
        font.setPointSize(12)
        self.username_line_edit.setFont(font)
        self.username_line_edit.setAlignment(Qt.AlignCenter)
        self.password_line_edit = QLineEdit(self.central_widget)
        self.password_line_edit.setObjectName(u"password_line_edit")
        self.password_line_edit.setGeometry(QRect(90, 150, 291, 31))
        self.password_line_edit.setFont(font)
        self.password_line_edit.setAlignment(Qt.AlignCenter)
        self.username_label = QLabel(self.central_widget)
        self.username_label.setObjectName(u"username_label")
        self.username_label.setGeometry(QRect(90, 40, 281, 31))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setItalic(False)
        font1.setWeight(75)
        self.username_label.setFont(font1)
        self.username_label.setAlignment(Qt.AlignCenter)
        self.password_label = QLabel(self.central_widget)
        self.password_label.setObjectName(u"password_label")
        self.password_label.setGeometry(QRect(90, 120, 281, 31))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setWeight(75)
        font2.setStrikeOut(False)
        self.password_label.setFont(font2)
        self.password_label.setAlignment(Qt.AlignCenter)
        self.login_button = QPushButton(self.central_widget)
        self.login_button.setObjectName(u"login_button")
        self.login_button.setGeometry(QRect(140, 220, 191, 41))
        font3 = QFont()
        font3.setPointSize(12)
        font3.setBold(False)
        font3.setWeight(50)
        self.login_button.setFont(font3)
        self.register_button = QPushButton(self.central_widget)
        self.register_button.setObjectName(u"register_button")
        self.register_button.setGeometry(QRect(160, 270, 151, 41))
        self.register_button.setFont(font3)
        main_window.setCentralWidget(self.central_widget)
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName(u"statusbar")
        main_window.setStatusBar(self.statusbar)

        self.translate_ui(main_window)

        QMetaObject.connectSlotsByName(main_window)

    def translate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "main_window"))
        self.username_label.setText(QCoreApplication.translate("MainWindow", u"Username", None))
        self.password_label.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.login_button.setText(QCoreApplication.translate("MainWindow", u"Login", None))
        self.register_button.setText(QCoreApplication.translate("MainWindow", u"Register", None))

        self.login_button.clicked.connect(self.send_function)
        self.register_button.clicked.connect(lambda: self.register("Yes"))

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (SERVER_IP, SERVER_PORT)
        client_sock.connect(server_address)
        self.client_socket = client_sock

    def send_function(self):
        self.client_socket.sendall(f"1@@{self.username_line_edit.text()},{self.password_line_edit.text()}".encode())
        return_code = self.client_socket.recv(1024).decode()
        print(return_code)
        if return_code == "1":
            # run main whatsapp
            self.window = QtWidgets.QMainWindow()
            ui = Ui_MainWhatsapp()
            ui.setupUi(self.window, self.username_line_edit.text(), self.client_socket)
            # main_window.show()
            self.window.show()

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
    main_window = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setupUi(main_window)
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
