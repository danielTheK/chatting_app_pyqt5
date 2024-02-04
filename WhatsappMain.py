# Import necessary modules
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import json
import sys
import multiprocessing
import enchant
from enchant import tokenize
from enchant.errors import TokenizerNotFoundError

# pylint: disable=no-name-in-module
from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent, QThread, pyqtSlot, QTimer, pyqtSignal
from PyQt5.QtGui import (QFocusEvent, QSyntaxHighlighter, QTextBlockUserData,
                         QTextCharFormat, QTextCursor, QPalette, QColor)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QMenu,
                             QPlainTextEdit, QVBoxLayout)
from enchant.utils import trim_suggestions

CHATS = {}




class SpellTextEdit(QPlainTextEdit):
    """QPlainTextEdit subclass which does spell-checking using PyEnchant"""

    # Clamping value for words like "regex" which suggest so many things that
    # the menu runs from the top to the bottom of the screen and spills over
    # into a second column.
    max_suggestions = 20

    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

        # Start with a default dictionary based on the current locale.
        self.highlighter = EnchantHighlighter(self.document())
        self.highlighter.setDict(enchant.Dict("en_us"))

    def contextMenuEvent(self, event):
        """Custom context menu handler to add a spelling suggestions submenu"""
        popup_menu = self.createSpellcheckContextMenu(event.pos())
        popup_menu.exec_(event.globalPos())

        # Fix bug observed in Qt 5.2.1 on *buntu 14.04 LTS where:
        # 1. The cursor remains invisible after closing the context menu
        # 2. Keyboard input causes it to appear, but it doesn't blink
        # 3. Switching focus away from and back to the window fixes it
        self.focusInEvent(QFocusEvent(QEvent.FocusIn))

    def createSpellcheckContextMenu(self, pos):
        """Create and return an augmented default context menu.
        This may be used as an alternative to the QPoint-taking form of
        ``createStandardContextMenu`` and will work on pre-5.5 Qt.
        """
        try:  # Recommended for Qt 5.5+ (Allows contextual Qt-provided entries)
            menu = self.createStandardContextMenu(pos)
        except TypeError:  # Before Qt 5.5
            menu = self.createStandardContextMenu()

        # Add a submenu for setting the spell-check language
        menu.addSeparator()
        menu.addMenu(self.createLanguagesMenu(menu))
        menu.addMenu(self.createFormatsMenu(menu))

        # Try to retrieve a menu of corrections for the right-clicked word
        spell_menu = self.createCorrectionsMenu(
            self.cursorForMisspelling(pos), menu)

        if spell_menu:
            menu.insertSeparator(menu.actions()[0])
            menu.insertMenu(menu.actions()[0], spell_menu)

        return menu

    def createCorrectionsMenu(self, cursor, parent=None):
        """Create and return a menu for correcting the selected word."""
        if not cursor:
            return None

        text = cursor.selectedText()
        suggests = trim_suggestions(text,
                                    self.highlighter.dict().suggest(text),
                                    self.max_suggestions)

        spell_menu = QMenu('Spelling Suggestions', parent)
        for word in suggests:
            action = QAction(word, spell_menu)
            action.setData((cursor, word))
            spell_menu.addAction(action)

        # Only return the menu if it's non-empty
        if spell_menu.actions():
            spell_menu.triggered.connect(self.cb_correct_word)
            return spell_menu

        return None

    def createLanguagesMenu(self, parent=None):
        """Create and return a menu for selecting the spell-check language."""
        curr_lang = self.highlighter.dict().tag
        lang_menu = QMenu("Language", parent)
        lang_actions = QActionGroup(lang_menu)

        for lang in enchant.list_languages():
            action = lang_actions.addAction(lang)
            action.setCheckable(True)
            action.setChecked(lang == curr_lang)
            action.setData(lang)
            lang_menu.addAction(action)

        lang_menu.triggered.connect(self.cb_set_language)
        return lang_menu

    def createFormatsMenu(self, parent=None):
        """Create and return a menu for selecting the spell-check language."""
        fmt_menu = QMenu("Format", parent)
        fmt_actions = QActionGroup(fmt_menu)

        curr_format = self.highlighter.chunkers()
        for name, chunkers in (('Text', []), ('HTML', [tokenize.HTMLChunker])):
            action = fmt_actions.addAction(name)
            action.setCheckable(True)
            action.setChecked(chunkers == curr_format)
            action.setData(chunkers)
            fmt_menu.addAction(action)

        fmt_menu.triggered.connect(self.cb_set_format)
        return fmt_menu

    def cursorForMisspelling(self, pos):
        """Return a cursor selecting the misspelled word at ``pos`` or ``None``
        This leverages the fact that QPlainTextEdit already has a system for
        processing its contents in limited-size blocks to keep things fast.
        """
        cursor = self.cursorForPosition(pos)
        misspelled_words = getattr(cursor.block().userData(), 'misspelled', [])

        # If the cursor is within a misspelling, select the word
        for (start, end) in misspelled_words:
            if start <= cursor.positionInBlock() <= end:
                block_pos = cursor.block().position()

                cursor.setPosition(block_pos + start, QTextCursor.MoveAnchor)
                cursor.setPosition(block_pos + end, QTextCursor.KeepAnchor)
                break

        if cursor.hasSelection():
            return cursor
        else:
            return None

    def cb_correct_word(self, action):  # pylint: disable=no-self-use
        """Event handler for 'Spelling Suggestions' entries."""
        cursor, word = action.data()

        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(word)
        cursor.endEditBlock()

    def cb_set_language(self, action):
        """Event handler for 'Language' menu entries."""
        lang = action.data()
        self.highlighter.setDict(enchant.Dict(lang))

    def cb_set_format(self, action):
        """Event handler for 'Language' menu entries."""
        chunkers = action.data()
        self.highlighter.setChunkers(chunkers)
        # TODO: Emit an event so this menu can trigger other things


class EnchantHighlighter(QSyntaxHighlighter):
    """QSyntaxHighlighter subclass which consults a PyEnchant dictionary"""
    tokenizer = None
    token_filters = (tokenize.EmailFilter, tokenize.URLFilter)

    # Define the spellcheck style once and just assign it as necessary
    # XXX: Does QSyntaxHighlighter.setFormat handle keeping this from
    #      clobbering styles set in the data itself?
    err_format = QTextCharFormat()
    err_format.setUnderlineColor(Qt.red)
    err_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)

        # Initialize private members
        self._sp_dict = None
        self._chunkers = []

    def chunkers(self):
        """Gets the chunkers in use"""
        return self._chunkers

    def dict(self):
        """Gets the spelling dictionary in use"""
        return self._sp_dict

    def setChunkers(self, chunkers):
        """Sets the list of chunkers to be used"""
        self._chunkers = chunkers
        self.setDict(self.dict())
        # FIXME: Revert self._chunkers on failure to ensure consistent state

    def setDict(self, sp_dict):
        """Sets the spelling dictionary to be used"""
        try:
            self.tokenizer = tokenize.get_tokenizer(sp_dict.tag,
                                                    chunkers=self._chunkers, filters=self.token_filters)
        except TokenizerNotFoundError:
            # Fall back to the "good for most euro languages" English tokenizer
            self.tokenizer = tokenize.get_tokenizer(
                chunkers=self._chunkers, filters=self.token_filters)
        self._sp_dict = sp_dict

        self.rehighlight()

    def highlightBlock(self, text):
        """Overridden QSyntaxHighlighter method to apply the highlight"""
        if not self._sp_dict:
            return

        # Build a list of all misspelled words and highlight them
        misspellings = []
        for (word, pos) in self.tokenizer(text):
            if not self._sp_dict.check(word):
                self.setFormat(pos, len(word), self.err_format)
                misspellings.append((pos, pos + len(word)))

        # Store the list so the context menu can reuse this tokenization pass
        # (Block-relative values so editing other blocks won't invalidate them)
        data = QTextBlockUserData()
        data.misspelled = misspellings
        self.setCurrentBlockUserData(data)


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


class Ui_MainWhatsapp(object):
    def setupUi(self, MainWhatsapp, name, client_sock):
        self.name = name
        self.client_sock = client_sock
        self.MainWindow = MainWhatsapp
        self.client_sock.sendall("first".encode())
        history = self.client_sock.recv(1024).decode()
        MainWhatsapp.setObjectName("MainWhatsapp")
        MainWhatsapp.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWhatsapp)
        self.centralwidget.setObjectName("centralwidget")

        # Contacts List
        self.contacts = QtWidgets.QListWidget(self.centralwidget)
        self.contacts.setGeometry(QtCore.QRect(0, 60, 211, 491))
        self.contacts.setObjectName("contacts")

        # Update Contacts Button
        self.updateContacts = QtWidgets.QPushButton(self.centralwidget)
        self.updateContacts.setGeometry(QtCore.QRect(0, 0, 211, 61))
        self.updateContacts.setObjectName("updateContacts")
        self.updateContacts.setText("Update contacts")

        # Current Contact Label
        self.currentContact = QtWidgets.QLabel(self.centralwidget)
        self.currentContact.setGeometry(QtCore.QRect(210, 0, 591, 61))
        self.currentContact.setObjectName("currentContact")

        # Chat List
        self.message_list = QtWidgets.QListWidget(self.centralwidget)
        self.message_list.setGeometry(QtCore.QRect(210, 60, 591, 380))
        self.message_list.setObjectName("chat")

        # Text Edit for typing messages
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(210, 440, 481, 81))
        self.textEdit.setObjectName("textEdit")

        # Send Button
        self.sendButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendButton.setGeometry(QtCore.QRect(690, 440, 111, 81))
        self.sendButton.setObjectName("sendButton")
        MainWhatsapp.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWhatsapp)
        QtCore.QMetaObject.connectSlotsByName(MainWhatsapp)
        self.sendUpdateContact()
        self.default_widget_size = 0
        if "$$$" not in history:
            global CHATS
            CHATS = json.loads(history)

    def retranslateUi(self, MainWhatsapp):
        self.run_thread_receiving_packets()  # starting the thread for receiving packets
        _translate = QtCore.QCoreApplication.translate
        MainWhatsapp.setWindowTitle(_translate("MainWhatsapp", "MainWindow"))
        self.sendButton.setText(_translate("MainWhatsapp", "Send"))
        self.contacts.setSortingEnabled(False)
        self.currentContact.setText("")
        self.currentContact.setFont(QtGui.QFont('Arial', 16))
        self.currentContact.setAlignment(QtCore.Qt.AlignCenter)
        # connections:
        self.updateContacts.clicked.connect(self.sendUpdateContact)
        self.sendButton.clicked.connect(self.sendMessage)
        self.contacts.itemSelectionChanged.connect(self.changeCurrentContact)

    def sendMessage(self):
        text = self.textEdit.toPlainText()
        CHATS[self.currentContact.text()].append(f"{self.name}@{text}")

        self.addMessage(self.name, text)

        text = f"{self.currentContact.text()}@{text}"
        self.client_sock.sendall(text.encode())

    def change_contacts_order(self, name):
        """for i in range(self.contacts.__len__()):
            if self.contacts.item(i).text() =="""
        pass

    def addMessage(self, name, message):
        message_widget = MessageWidget(f"{name}:", message)
        self.returnWidgetsToNormal()
        message_item = QtWidgets.QListWidgetItem(self.message_list)
        message_item.setSizeHint(message_widget.sizeHint() + message_widget.reply_button.sizeHint())
        if name == self.name:
            message_item.setBackground(QColor(20,255,20))
        else:
            message_item.setBackground(QColor(255,0,0))
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
            self.add_to_CHATS(i)

    def add_to_CHATS(self, name):
        if name not in CHATS:
            CHATS[name] = []

    def changeCurrentContact(self):
        if len(self.contacts.selectedItems()) != 0:
            name = self.contacts.selectedItems()[0].text()
            self.currentContact.setText(name)
            for i in range(self.contacts.count()):
                if self.contacts.item(i).text() == name:
                    self.contacts.item(i).setIcon(QtGui.QIcon())

            self.message_list.clear()

            for i in CHATS[name]:
                self.addMessage(*i.split("@"))

    def addIcon(self, name):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../Downloads/Exclamation mark.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        for i in range(self.contacts.count()):
            if self.contacts.item(i).text() == name and name != self.currentContact.text():
                self.contacts.item(i).setIcon(icon)


class receiving_packets(QThread):
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
            if "$$" == str(message[0:2]):
                self.contacts_message.emit(message[2:])
            if "@" in message:
                name, content = message.split("@")
                content = content[:-1]
                self.obj.addIcon(name)

                CHATS[name].append(message)
                if name == self.obj.currentContact.text():
                    print(f"{content = }")
                    self.normal_message.emit(name, content)
