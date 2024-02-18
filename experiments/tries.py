import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QListWidget, QListWidgetItem, \
    QPushButton, QHBoxLayout, QGridLayout
from playsound import playsound
import threading
from mutagen.mp3 import MP3


class VoiceMessageWidget(QtWidgets.QWidget):
    def __init__(self, path):
        self.path = path
        super().__init__()
        self.filename_label = QLabel(f"File: {path.split('/')[-1]}")
        self.play_button = QPushButton("Download")
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.filename_label, 0, 0)
        self.layout.addWidget(self.play_button, 0, 1)
        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar, 1, 0)
        self.play_button.clicked.connect(self.start_playing)

    def update_progress_bar(self, duration):
        self.progress_bar.setMaximum(int(duration))
        for i in range(0, int(duration) + 1):
            self.progress_bar.setValue(i)
            threading.Event().wait(1)

    def play(self):
        playsound(self.path)

    def start_playing(self):
        audio = MP3(self.path)
        threading.Thread(target=self.play).start()
        threading.Thread(target=self.update_progress_bar, args=[audio.info.length]).start()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.voice_list = QListWidget()
        self.add_message_button = QPushButton("Add Voice Message")
        self.add_message_button.clicked.connect(self.add_voice_message)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.voice_list)
        self.layout.addWidget(self.add_message_button)

        self.setLayout(self.layout)

    def add_voice_message(self):
        message_widget = VoiceMessageWidget("house_lo.mp3")
        list_item = QListWidgetItem()
        list_item.setSizeHint(message_widget.sizeHint())
        self.voice_list.addItem(list_item)
        self.voice_list.setItemWidget(list_item, message_widget)


if __name__ == "__main__":
    """app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.setWindowTitle("Voice Message Player")
    main_window.setGeometry(100, 100, 400, 300)
    main_window.show()

    sys.exit(app.exec_())"""
    pass
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QGridLayout
from PyQt5.QtGui import QFont

class EmojiWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Emoji")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        emojis = ["😀", "😂", "😊", "😎", "😍", "😜", "🤔", "😴"]  # Add more emojis as needed
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
        if isinstance(self.parent(), LabelWindow):
            self.parent().set_selected_emoji(emoji)
        self.close()

class LabelWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emoji Selector")
        self.label = QLabel("No Emoji Selected")
        self.button = QPushButton("Select Emoji")
        self.button.clicked.connect(self.open_emoji_window)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def open_emoji_window(self):
        emoji_window = EmojiWindow(self)
        emoji_window.exec_()

    def set_selected_emoji(self, emoji):
        self.label.setText(emoji)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = LabelWindow()
    main_window.show()
    sys.exit(app.exec_())
