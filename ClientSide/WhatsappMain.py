# Import necessary modules
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import json
import sys
import multiprocessing

# pylint: disable=no-name-in-module
from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent, QThread, pyqtSlot, QTimer, pyqtSignal
from PyQt5.QtGui import (QFocusEvent, QSyntaxHighlighter, QTextBlockUserData,
                         QTextCharFormat, QTextCursor, QPalette, QColor)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QMenu,
                             QPlainTextEdit, QVBoxLayout)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

chats = {}


class FileWidget(QtWidgets.QWidget):
    def __init__(self, filename, filesize):
        super(FileWidget, self).__init__()
        self.file_name = filename
        self.filename_label = QLabel(f"File: {filename}")
        self.filesize_label = QLabel(f"Size: {float(filesize):.2f} MB")
        self.download_button = QPushButton("Download")
        self.download_button.setIcon(QIcon("images/download_icon.jpg"))
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.filesize_label)
        self.layout.addWidget(self.download_button)

        self.download_button.clicked.connect(self.start_download)

    def start_download(self):
        print(f"The file {self.file_name} is downloading!")


class MessageWidget(QtWidgets.QWidget):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.title_label = QtWidgets.QLabel(title)
        self.message_label = QtWidgets.QLabel(message)
        self.reply_button = QtWidgets.QPushButton("Reply")
        self.delete_button = QtWidgets.QPushButton("Delete")

        self.reply_button.clicked.connect(self.showReplyDialog)
        self.delete_button.clicked.connect(self.showDeleteConfirmation)

        self.reply_button.setVisible(False)
        self.delete_button.setVisible(False)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.reply_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

    def showReplyDialog(self):
        reply_dialog = QtWidgets.QDialog(self)
        reply_dialog.setWindowTitle("Reply")

        layout = QtWidgets.QVBoxLayout(reply_dialog)
        reply_edit = QtWidgets.QLineEdit(reply_dialog)
        layout.addWidget(reply_edit)

        reply_button = QtWidgets.QPushButton("Send", reply_dialog)
        reply_button.clicked.connect(lambda: self.replyClicked(reply_edit.text(), reply_dialog))
        layout.addWidget(reply_button)

        reply_dialog.exec_()

    def replyClicked(self, reply_text, reply_dialog):
        print(f"Reply: {reply_text}")
        reply_dialog.accept()

    def showDeleteConfirmation(self):
        reply = QtWidgets.QMessageBox.question(self, 'Delete Message', 'Are you sure you want to delete this message?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            print(f"Deleted message: {self.message_label.text()}")

    def showOptions(self):
        self.reply_button.setVisible(True)
        self.delete_button.setVisible(True)

    def hideOptions(self):
        self.reply_button.setVisible(False)
        self.delete_button.setVisible(False)


app = QtWidgets.QApplication(sys.argv)
size = app.primaryScreen().availableGeometry()
width, height = size.width(), size.height()
print(f"{height = }, {width = }")
height_ratio = height / 1080
width_ratio = width / 1920
# trying to make it better
height_ratio *= 1.55
width_ratio *= 1.75


class Ui_MainWhatsapp(object):
    def __init__(self):
        self.message_selection = None
        self.currentContact = None
        self.default_widget_size = None
        self.statusbar = None
        self.updateContacts = None
        self.sendButton = None
        self.textEdit = None
        self.message_list = None
        self.contacts = None
        self.central_widget = None
        self.client_sock = None
        self.name = None
        self.MainWhatsapp = None

    def setupUi(self, MainWhatsapp, name, client_sock):
        self.name = name
        self.client_sock = client_sock
        self.MainWhatsapp = MainWhatsapp
        self.client_sock.sendall("first".encode())
        history = self.client_sock.recv(1024).decode()
        MainWhatsapp.resize(int(800 * width_ratio), int(600 * height_ratio))
        self.central_widget = QWidget(MainWhatsapp)
        self.central_widget.setObjectName(u"central_widget")

        self.contacts = QListWidget(self.central_widget)
        self.contacts.setObjectName(u"contacts")
        self.contacts.setGeometry(
            QRect(int(10 * width_ratio), int(40 * height_ratio), int(221 * width_ratio), int(531 * height_ratio)))

        self.message_list = QListWidget(self.central_widget)
        self.message_list.setObjectName(u"message_list")
        self.message_list.setGeometry(
            QRect(int(230 * width_ratio), int(10 * height_ratio), int(551 * width_ratio), int(501 * height_ratio)))

        self.textEdit = QTextEdit(self.central_widget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(
            QRect(int(230 * width_ratio), int(510 * height_ratio), int(481 * width_ratio), int(61 * height_ratio)))

        self.sendButton = QPushButton(self.central_widget)
        self.sendButton.setObjectName(u"sendButton")
        self.sendButton.setGeometry(QRect(int(710 * width_ratio), int(530 * height_ratio), int(71 * width_ratio), int(41 * height_ratio)))
        self.sendButton.setIcon(QIcon("images/send_icon.png"))
        self.sendButton.setIconSize(QSize(self.sendButton.width(), self.sendButton.height())) # size dont fit, button size is 62 30, need to find better image or change the size or the button

        self.updateContacts = QPushButton(self.central_widget)
        self.updateContacts.setObjectName(u"updateContacts")
        self.updateContacts.setGeometry(
            QRect(int(10 * width_ratio), int(10 * height_ratio), int(221 * width_ratio), int(31 * height_ratio)))

        self.currentContact = QtWidgets.QLabel(self.central_widget)
        self.currentContact.setGeometry(
            QtCore.QRect(int(210 * width_ratio), 0, int(591 * width_ratio), int(61 * height_ratio)))
        self.currentContact.setObjectName("currentContact")

        self.message_selection = QtWidgets.QComboBox(self.central_widget)
        self.message_selection.addItem("")
        self.message_selection.addItem("")
        self.message_selection.addItem("")
        self.message_selection.setObjectName(u"message_selection")
        self.message_selection.setGeometry(
            QRect(int(710 * width_ratio), int(510 * height_ratio), int(71 * width_ratio), int(21 * height_ratio)))
        self.message_selection.setEditable(False)

        MainWhatsapp.setCentralWidget(self.central_widget)

        MainWhatsapp.setCentralWidget(self.central_widget)
        self.statusbar = QStatusBar(MainWhatsapp)
        self.statusbar.setObjectName(u"statusbar")
        MainWhatsapp.setStatusBar(self.statusbar)

        self.translate_ui(MainWhatsapp)
        QtCore.QMetaObject.connectSlotsByName(MainWhatsapp)
        self.sendUpdateContact()
        self.default_widget_size = 0
        if "$$$" not in history:
            global chats
            chats = json.loads(history)
            print(f'{chats = }')

    def translate_ui(self, MainWhatsapp):
        self.run_thread_receiving_packets()  # starting the thread for receiving packets
        _translate = QtCore.QCoreApplication.translate
        MainWhatsapp.setWindowTitle(QCoreApplication.translate("MainWhatsapp", u"MainWhatsapp", None))
        self.textEdit.setHtml(QCoreApplication.translate("MainWhatsapp",
                                                         u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                         "p, li { white-space: pre-wrap; }\n"
                                                         "</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
                                                         "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>",
                                                         None))
        self.textEdit.setPlaceholderText(QCoreApplication.translate("MainWhatsapp", u"Enter message...", None))
        self.sendButton.setText(QCoreApplication.translate("MainWhatsapp", u"Send", None))
        self.updateContacts.setText(QCoreApplication.translate("MainWhatsapp", u"Update Contacts", None))
        self.currentContact.setText("")
        self.currentContact.setFont(QtGui.QFont('Arial', 16))
        self.currentContact.setAlignment(Qt.AlignCenter)
        self.message_selection.setItemText(0, QCoreApplication.translate("MainWhatsapp", u"File", None))
        self.message_selection.setItemText(1, QCoreApplication.translate("MainWhatsapp", u"Voice", None))
        self.message_selection.setItemText(2, QCoreApplication.translate("MainWhatsapp", u"Image", None))
        self.message_selection.activated.connect(self.send_files_images_voice)
        # connections:
        self.updateContacts.clicked.connect(self.sendUpdateContact)
        self.sendButton.clicked.connect(self.sendMessage)
        self.contacts.itemSelectionChanged.connect(self.changeCurrentContact)

    def sendMessage(self):
        text = self.textEdit.toPlainText()
        if text != "":
            chats[self.currentContact.text()].append(f"{self.name}@{text}")

            self.addMessage(self.name, text)

            text = f"{self.currentContact.text()}@{text}"
            self.client_sock.sendall(text.encode())

    def change_contacts_order(self, name):
        """for i in range(self.contacts.__len__()):
            if self.contacts.item(i).text() =="""
        pass

    def addMessage(self, name, message):
        message_widget = MessageWidget(f"{name}:", message)
        #self.returnWidgetsToNormal() no need for that for now, only when and if we will add buttons to messeges
        message_item = QtWidgets.QListWidgetItem(self.message_list)
        message_item.setSizeHint(message_widget.sizeHint() + message_widget.reply_button.sizeHint())
        if name == self.name:
            message_item.setBackground(QColor(20, 255, 20))
        else:
            message_item.setBackground(QColor(255, 0, 0))
        if self.default_widget_size == 0:
            self.default_widget_size = message_item.sizeHint()
        # this is the problem:
        self.message_list.setItemWidget(message_item, message_widget)

    def returnWidgetsToNormal(self):
        for i in range(self.message_list.count()):
            temp_item = self.message_list.itemWidget(self.message_list.item(i))
            if temp_item is not None:
                temp_item.hideOptions()
                self.message_list.item(i).setSizeHint(self.default_widget_size)

    def run_thread_receiving_packets(self):
        self.thread = receiving_packets(self)
        self.thread.start()
        self.thread.normal_message.connect(self.addMessage)
        self.thread.contacts_message.connect(self.update_contacts)
        self.thread.notify_message.connect(self.add_notifies)

    def sendUpdateContact(self):
        self.client_sock.sendall("121212".encode())

    def update_contacts(self, contacts):
        print(self.contacts.selectedItems())

        try:
            self.contacts.clear()
        except:
            pass

        for i in contacts.split(","):
            item = QtWidgets.QListWidgetItem()
            item.setText(i)
            self.contacts.addItem(item)
            print(i)
            self.add_to_CHATS(i)

    def add_to_CHATS(self, name):
        if name not in chats:
            chats[name] = []

    def changeCurrentContact(self):
        if len(self.contacts.selectedItems()) != 0:
            name = self.contacts.selectedItems()[0].text()
            self.currentContact.setText(name)
            for i in range(self.contacts.count()):
                if self.contacts.item(i).text() == name:
                    self.contacts.item(i).setIcon(QtGui.QIcon())

            self.message_list.clear()

            for i in chats[name]:
                if i[:3] == "8$$":
                    self.add_notifies(i.split("@")[1], i.split("@")[2])
                    continue
                self.addMessage(*i.split("@"))

    def send_files_images_voice(self):
        file_path, _ = QFileDialog.getOpenFileName()
        if file_path:
            with open(file_path, "rb") as f:
                file_data = f.read()
            self.client_sock.sendall(
                f"7$${self.currentContact.text()}@{file_path.split('/')[-1]}@{str(len(file_data) / 1048576)}@".encode() + file_data + b"$$END$$")
            # protocol: 7$$sent_to@file_name@file_size@file_data$$END$$
            self.add_notifies(file_path.split("/")[-1], len(file_data) / 1048576)
            chats[self.currentContact.text()].append(f"8$${self.currentContact.text()}@{file_path.split('/')[-1]}@{str(len(file_data) / 1048576)}")

    def add_notifies(self, file_name, size):
        message_widget = FileWidget(file_name, size)
        message_item = QtWidgets.QListWidgetItem(self.message_list)
        message_item.setSizeHint(message_widget.sizeHint())
        message_item.setBackground(QColor(200, 200, 200))  # thats makes the background gray
        """if name == self.name:
            message_item.setBackground(QColor(20, 255, 20))
        else:
            message_item.setBackground(QColor(255, 0, 0))
        if self.default_widget_size == 0:
            self.default_widget_size = message_item.sizeHint()"""
        self.message_list.setItemWidget(message_item, message_widget)

    def addIcon(self, name):
        icon = QtGui.QIcon("images/Exclamation_mark.jpg")
        for i in range(self.contacts.count()):
            if self.contacts.item(i).text() == name and name != self.currentContact.text():
                self.contacts.item(i).setIcon(icon)


class receiving_packets(QThread):
    notify_message = pyqtSignal(str, str)
    normal_message = pyqtSignal(str, str)
    contacts_message = pyqtSignal(str)

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def run(self):
        while True:
            print("receiving_packets is running")
            message = self.obj.client_sock.recv(1024).decode()
            print(f"{message = }")
            if message[:3] == "8$$":  # protocal: 8$$sender@file_name@file_size
                print(message[3:])
                name, file_name, file_size = message[3:].split("@")
                self.obj.addIcon(name)
                chats[name].append(message)
                if name == self.obj.currentContact.text():
                    self.notify_message.emit(file_name, file_size)
                continue
            if "$$" == str(message[0:2]):
                self.contacts_message.emit(message[2:])
                continue
            if "@" in message:
                name, content = message.split("@")
                content = content[:-1]
                self.obj.addIcon(name)
                chats[name].append(message)
                if name == self.obj.currentContact.text():
                    print(f"{content = }")
                    self.normal_message.emit(name, content)
                continue
