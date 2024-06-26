# Import necessary modules
import os
import time
import wave

import pyaudio
from PyQt5 import QtGui
import json
import sys

# pylint: disable=no-name-in-module
from PyQt5.Qt import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

chats = {}
drafts = {}
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QListWidget, QPushButton, QHBoxLayout, QGridLayout, QDialog
from playsound import playsound
import threading
from mutagen.mp3 import MP3

MAX_RECORDING_TIME = 10

import soundfile as sf
from lameenc import Encoder


class users_window(object):
    def setupUi(self, MainWindow, users, messages, send_function):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(241, 350)
        self.window = MainWindow
        self.send_function = send_function
        self.messages = messages
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.usersList = QtWidgets.QListWidget(self.centralwidget)
        self.usersList.setGeometry(QtCore.QRect(0, 30, 241, 271))
        self.usersList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.usersList.setObjectName("usersList")
        self.selectButton = QtWidgets.QPushButton(self.centralwidget)
        self.selectButton.setGeometry(QtCore.QRect(0, 0, 241, 31))
        self.selectButton.setObjectName("selectButton")
        self.selectButton.pressed.connect(self.send_to_all)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 241, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        for i in users:
            item = QtWidgets.QListWidgetItem()
            item.setText(i)
            self.usersList.addItem(item)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.usersList.setSortingEnabled(False)
        __sortingEnabled = self.usersList.isSortingEnabled()
        self.usersList.setSortingEnabled(False)
        self.usersList.setSortingEnabled(__sortingEnabled)
        self.selectButton.setText(_translate("MainWindow", "select"))
        self.selectButton.setShortcut(_translate("MainWindow", "Return"))

    def send_to_all(self):
        for item in self.usersList.selectedItems():
            for text in self.messages:
                self.send_function(item.text(), text)
        self.window.close()


class MessagesTree(QListWidget):
    def __init__(self, changetoolbar, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.change_toolbar = changetoolbar

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            item.setSelected(not item.isSelected())
            self.change_toolbar(len(self.selectedItems()))


class AudioRecorder(QThread):
    finished = pyqtSignal()

    def __init__(self, parent=None, chunk=3024, frmat=pyaudio.paInt16, channels=2, rate=44100):
        super().__init__(parent)
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.is_recording = True
        self.recording_time = 0

    def run(self):
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                  input=True, frames_per_buffer=self.CHUNK)

        self.frames = []
        timer = QTimer()
        timer.timeout.connect(self.update_recording_time)
        timer.start(1000)  # Update every second
        while self.is_recording:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

    def update_recording_time(self):
        self.recording_time += 1

    def stop_recording(self):
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.save_recording()

    def save_recording(self):
        wf = wave.open('a.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.frames = []


class return_every_second(QThread):
    update = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(MAX_RECORDING_TIME):
            self.update.emit(i)
            threading.Event().wait(1)


class RecorderWidget(QWidget):
    end_recording = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        self.label = QLabel("Recording Time: 0 seconds")
        self.stop_button = QPushButton("Stop Recording")
        self.recorder = None

        layout.addWidget(self.label,0,0)
        layout.addWidget(self.stop_button,0,1)

        self.stop_button.clicked.connect(self.stop_recording)

    def start_recording(self):
        self.recorder = AudioRecorder()
        self.recorder.start()
        self.thread = return_every_second()
        self.thread.start()
        self.thread.update.connect(self.update_time)

    def update_time(self, num):
        self.label.setText(f"Recording Time: {num} seconds")
        if num == MAX_RECORDING_TIME - 1:
            self.stop_recording()

    def stop_recording(self):
        time.sleep(0.5)
        self.recorder.stop_recording()
        self.thread.blockSignals(True)
        self.end_recording.emit()


class update_progress_bar(QThread):
    update = pyqtSignal(int)

    def __init__(self, duration):
        super().__init__()
        self.duration = duration

    def run(self):
        for i in range(self.duration + 1):
            self.update.emit(i)
            threading.Event().wait(0.1)


class VoiceMessageWidget(QtWidgets.QWidget):
    def __init__(self, path):
        self.path = path
        super().__init__()
        self.filename_label = QLabel(f"File: {path.split('/')[-1]}")
        self.play_button = QPushButton("Play")
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.filename_label, 0, 0)
        self.layout.addWidget(self.play_button, 0, 1)
        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar, 1, 0)
        self.play_button.clicked.connect(self.start_playing)

    def update_progress_bar(self, num):
        self.progress_bar.setValue(num)

    def play(self):
        playsound(self.path)

    def start_playing(self):
        audio = MP3(self.path)
        self.progress_bar.setMaximum(int(audio.info.length) * 10)
        threading.Thread(target=self.play).start()
        self.thread = update_progress_bar(int(audio.info.length) * 10)
        self.thread.start()
        self.thread.update.connect(self.update_progress_bar)


class FileWidget(QtWidgets.QWidget):
    def __init__(self, filename, filesize, id, sock):
        self.id = id
        self.sock = sock
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
        if self.id != -99:
            self.sock.sendall(f"6$${self.id}".encode())
        print(self.id)


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
        reply_dialog.accept()

    def showDeleteConfirmation(self):
        reply = QtWidgets.QMessageBox.question(self, 'Delete Message', 'Are you sure you want to delete this message?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            pass

    def showOptions(self):
        self.reply_button.setVisible(True)
        self.delete_button.setVisible(True)

    def hideOptions(self):
        self.reply_button.setVisible(False)
        self.delete_button.setVisible(False)


class EmojiWindow(QDialog):
    def __init__(self, textEdit):
        self.textEdit = textEdit
        super().__init__()
        self.setWindowTitle("Select Emoji")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        emojis = ["😀", "😂", "😊", "😎", "😍", "😜", "🤔", "😴", "💪", "👍", "👌",
                  "😱", "🐶"]  # https://tools.picsart.com/text/emojis/
        row = 0
        col = 0
        for emoji in emojis:
            button = QPushButton(emoji)
            button.setFont(QFont("Arial", 20))
            button.clicked.connect(lambda _, e=emoji: self.select_emoji(e))
            self.layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def select_emoji(self, emoji):
        self.textEdit.setText(self.textEdit.toPlainText() + emoji)


app = QtWidgets.QApplication(sys.argv)
size = app.primaryScreen().availableGeometry()
width, height = size.width(), size.height()
print(f"{height = }, {width = }")
height_ratio = height / 1080
width_ratio = width / 1920
# trying to make it better
height_ratio *= 1.55
width_ratio *= 1.75

# messages_toolbar_actions:
PRINT_MESSAGES = 0
COPY_TO_CLIPBOARD = 1
PASS_MESSAGE = 2


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

        self.messages_layout = QGridLayout(self.central_widget)
        self.message_list = MessagesTree(self.change_messages_toolbar)
        self.messages_layout.addWidget(self.message_list, 1, 0)
        self.message_list.setFixedSize(int(551 * width_ratio), int(501 * height_ratio))
        self.messages_layout.setContentsMargins(int(230 * width_ratio), int(30 * height_ratio), 0, 0)
        self.messages_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.toolbar = QToolBar()
        self.toolbar.setHidden(True)

        print_selected_action = QAction("Print Selected", self.central_widget)
        print_selected_action.triggered.connect(lambda: self.messages_toolbar_actions(PRINT_MESSAGES))
        self.toolbar.addAction(print_selected_action)

        copy_selected_action = QAction("Copy", self.central_widget)
        copy_selected_action.triggered.connect(lambda: self.messages_toolbar_actions(COPY_TO_CLIPBOARD))
        self.toolbar.addAction(copy_selected_action)

        pass_selected_action = QAction("Forward", self.central_widget)
        pass_selected_action.triggered.connect(lambda: self.messages_toolbar_actions(PASS_MESSAGE))
        self.toolbar.addAction(pass_selected_action)

        self.messages_layout.addWidget(self.toolbar, 0, 0)

        self.textEdit = QTextEdit(self.central_widget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(
            QRect(int(280 * width_ratio), int(510 * height_ratio), int(481 * width_ratio), int(61 * height_ratio)))

        self.emoji_button = QPushButton(self.central_widget)
        self.emoji_button.setObjectName(u"emoji_button")
        self.emoji_button.setGeometry(
            QRect(int(230 * width_ratio), int(510 * height_ratio), int(50 * width_ratio), int(61 * height_ratio)))
        self.emoji_button.clicked.connect(self.open_emoji_window)

        self.sendButton = QPushButton(self.central_widget)
        self.sendButton.setObjectName(u"sendButton")
        self.sendButton.setGeometry(
            QRect(int(710 * width_ratio), int(530 * height_ratio), int(71 * width_ratio), int(41 * height_ratio)))
        self.sendButton.setIcon(QIcon("images/send_icon.png"))
        self.sendButton.setIconSize(QSize(self.sendButton.width(),
                                          self.sendButton.height()))  # size dont fit, button size is 62 30, need to find better image or change the size or the button

        self.updateContacts = QPushButton(self.central_widget)
        self.updateContacts.setObjectName(u"updateContacts")
        self.updateContacts.setGeometry(
            QRect(int(10 * width_ratio), int(10 * height_ratio), int(221 * width_ratio), int(31 * height_ratio)))

        self.currentContact = QtWidgets.QLabel(self.central_widget)
        self.currentContact.setGeometry(
            QtCore.QRect(int(210 * width_ratio), 0, int(591 * width_ratio), int(40 * height_ratio)))
        self.currentContact.setObjectName("currentContact")
        self.currentContact.mousePressEvent = self.open_user_data

        self.message_selection = QtWidgets.QComboBox(self.central_widget)
        self.message_selection.addItem("")
        self.message_selection.addItem("")
        self.message_selection.addItem("")
        self.message_selection.setObjectName(u"message_selection")
        self.message_selection.setGeometry(
            QRect(int(710 * width_ratio), int(510 * height_ratio), int(71 * width_ratio), int(21 * height_ratio)))
        self.message_selection.setEditable(False)

        self.record_widget = RecorderWidget(self.central_widget)
        self.record_widget.setHidden(True)
        self.record_widget.setGeometry(
            QRect(int(280 * width_ratio), int(510 * height_ratio), int(440 * width_ratio), int(61 * height_ratio)))

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
        print(f"{chats = }")

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
        self.textEdit.setPlainText("")
        if text != "":
            drafts[self.currentContact.text()] = ""
            self.send(self.currentContact.text(), text)

    def send(self, contact, message):
        chats[contact].append(f"{self.name}@{message}")
        self.addMessage(self.name, message)
        text = f"{contact}@{message}"
        self.client_sock.sendall(text.encode())
        self.move_item_up(contact)

    def addMessage(self, name, message):
        message_widget = MessageWidget(f"{name}:", message)
        message_item = QtWidgets.QListWidgetItem(self.message_list)
        message_item.setSizeHint(message_widget.sizeHint() + message_widget.reply_button.sizeHint())
        if name == self.name:
            message_item.setBackground(QColor(20, 255, 20))
            message_item.listWidget()
        else:
            message_item.setBackground(QColor(255, 0, 0))
        if self.default_widget_size == 0:
            self.default_widget_size = message_item.sizeHint()
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

        try:
            self.contacts.clear()
        except:
            pass

        for i in contacts.split(","):
            item = QtWidgets.QListWidgetItem()
            item.setText(i)
            self.contacts.addItem(item)
            self.add_to_CHATS(i)

    def add_to_CHATS(self, name):
        if name not in chats:
            chats[name] = []

    def changeCurrentContact(self):
        if self.textEdit.toPlainText() != "":
            drafts[self.currentContact.text()] = self.textEdit.toPlainText()
        if len(self.contacts.selectedItems()) != 0:
            name = self.contacts.selectedItems()[0].text()
            self.currentContact.setText(name)
            for i in range(self.contacts.count()):
                if self.contacts.item(i).text() == name:
                    self.contacts.item(i).setIcon(QtGui.QIcon())
                    break
            self.message_list.clear()
            if name in drafts:
                self.textEdit.setPlainText(drafts[name])
            else:
                self.textEdit.setPlainText("")
            for i in chats[name]:
                if i[:3] == "8$$":
                    arguments = i.split("@")
                    self.add_notifies(arguments[1], arguments[2], arguments[3])
                    continue
                self.addMessage(*i.split("@"))
            self.change_messages_toolbar(0)  # so the toolbar will become hidden

    def remove_record_widget(self):
        self.record_widget.setHidden(True)
        self.textEdit.setHidden(False)

    def messages_toolbar_actions(self, action):
        selected_items = self.message_list.selectedItems()
        if action == PRINT_MESSAGES:
            print("Selected items:")
            for item in selected_items:
                if type(self.message_list.itemWidget(item)) == FileWidget:
                    return  # for now it only works with simple MessageWidget
                print(self.message_list.itemWidget(item).message_label.text())
        elif action == COPY_TO_CLIPBOARD:
            all_texts = ""
            for item in selected_items:
                if type(self.message_list.itemWidget(item)) == FileWidget:
                    return  # for now it only works with simple MessageWidget
                all_texts += self.message_list.itemWidget(item).message_label.text()
            cb = QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(all_texts, mode=cb.Clipboard)
        elif action == PASS_MESSAGE:
            # open the users window to select who you want to pass to
            self.window = QtWidgets.QMainWindow()
            self.ui = users_window()
            all_texts = []
            for item in selected_items:
                if type(self.message_list.itemWidget(item)) == FileWidget:
                    return  # for now it only works with simple MessageWidget
                all_texts.append(self.message_list.itemWidget(item).message_label.text())
            self.ui.setupUi(self.window, [self.contacts.item(i).text() for i in range(self.contacts.count())],
                            all_texts, send_function=self.send)
            self.window.show()

    def send_files_images_voice(self, action):
        if action == 0:  # send file
            file_path, _ = QFileDialog.getOpenFileName()
            if file_path:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                self.client_sock.sendall(
                    f"7$${self.currentContact.text()}@@@{file_path.split('/')[-1]}@@@{str(len(file_data) / 1048576)}@@@".encode() + file_data + b"$$END$$")
                # protocol: 7$$sent_to@file_name@file_size@file_data$$END$$
                self.add_notifies(file_path.split("/")[-1], len(file_data) / 1048576)
                chats[self.currentContact.text()].append(
                    f"8$${self.currentContact.text()}@{file_path.split('/')[-1]}@{str(len(file_data) / 1048576)}")
        if action == 1:  # send recording
            self.record_widget.setHidden(False)
            self.textEdit.setHidden(True)
            self.record_widget.start_recording()
            self.record_widget.end_recording.connect(self.remove_record_widget)

    def add_notifies(self, file_name, size, file_id=-99):
        message_widget = FileWidget(file_name, size, file_id, self.client_sock)
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
        self.move_item_up(name)
        for i in range(self.contacts.count()):
            if self.contacts.item(i).text() == name and name != self.currentContact.text():
                self.contacts.item(i).setIcon(icon)

    def open_emoji_window(self):
        emoji_window = EmojiWindow(self.textEdit)
        emoji_window.exec_()

    def open_user_data(self, *args):  # placeholder, in case i want to add users data
        print(self.currentContact.text())

    def move_item_up(self, name):
        item = self.contacts.selectedItems()[0]
        for i in range(self.contacts.count()):
            if self.contacts.item(i).text() == name:
                selected_item = self.contacts.item(i)
                index = self.contacts.row(selected_item)
                if index > 0:
                    self.contacts.takeItem(index)
                    self.contacts.insertItem(0, selected_item.text())
                    self.contacts.setCurrentRow(0)
                break
        self.contacts.setCurrentItem(item)

    def change_messages_toolbar(self, num):
        self.toolbar.setHidden(num == 0)


class receiving_packets(QThread):
    notify_message = pyqtSignal(str, str, str)
    normal_message = pyqtSignal(str, str)
    contacts_message = pyqtSignal(str)

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def run(self):
        while True:
            print("receiving_packets is running")
            message = self.obj.client_sock.recv(1024)
            print(f"{message = }")
            if message[:4] == b"10$$":  # 10$${file_name}$${file}$$END$$
                file_name = message.split(b"$$")[1].decode()
                print(f"{file_name} is downloading!!")
                file_data = message[(4 + len(file_name) + 2):]  # skipping the name part of massage
                while file_data[-7:] != b"$$END$$":
                    file_data += self.obj.client_sock.recv(1024)
                file_data = file_data[:-7]
                with open(file_name, "wb") as f:
                    f.write(file_data)
                continue
            if message[:3] == b"8$$":  # protocal: 8$$sender@file_name@file_size@file_id
                name, file_name, file_size, file_id = message[3:].decode().split("@")
                self.obj.addIcon(name)
                chats[name].append(message.decode())
                if name == self.obj.currentContact.text():
                    self.notify_message.emit(file_name, file_size, file_id)
                continue
            if b"$$" == message[0:2]:
                self.contacts_message.emit(message[2:].decode())
                continue
            if b"@" in message:
                name, content = message.decode().split("@")
                content = content[:-1]
                self.obj.addIcon(name)
                chats[name].append(message.decode())
                if name == self.obj.currentContact.text():
                    self.normal_message.emit(name, content)
                continue
