"""import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QListWidget, QListWidgetItem, \
    QPushButton, QHBoxLayout, QGridLayout, QDialog
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
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.setWindowTitle("Voice Message Player")
    main_window.setGeometry(100, 100, 400, 300)
    main_window.show()

    sys.exit(app.exec_())
    pass
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTextEdit


class TextEdit(QTextEdit):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            print("save")


def main():
    app = QApplication([])

    w = TextEdit()
    w.show()

    app.exec_()


if __name__ == "__main__":
    main()
