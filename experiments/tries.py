"""import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QListWidget, QListWidgetItem, \
    QPushButton, QHBoxLayout, QGridLayout, QDialog
from playsound import playsound
import threading
from mutagen.mp3 import MP3

class update_progress_bar(QThread):
    update = pyqtSignal(int)

    def __init__(self, duration):
        super().__init__()
        self.duration = duration
    def run(self):
        for i in range(self.duration+1):
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
        self.progress_bar.setMaximum(int(audio.info.length)*10)
        threading.Thread(target=self.play).start()
        self.thread = update_progress_bar(int(audio.info.length)*10)
        self.thread.start()
        self.thread.update.connect(self.update_progress_bar)



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
    pass"""
import threading

"""class TextEdit(QTextEdit):
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
"""
"""import sys
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import time

MAX_RECORDING_TIME = 10


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
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Recording Time: 0 seconds")
        self.stop_button = QPushButton("Stop Recording")
        self.recorder = AudioRecorder()

        layout.addWidget(self.label)
        layout.addWidget(self.stop_button)

        self.stop_button.clicked.connect(self.stop_recording)

    def start_recording(self):
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
        message_widget = RecorderWidget()
        message_widget.start_recording()
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
"""
import sys
from PyQt5.QtWidgets import QApplication, QListWidget, QPushButton, QVBoxLayout, QWidget, QInputDialog

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list_widget = QListWidget()
        self.list_widget.addItems(["Item 1", "Item 2", "Item 3", "Item 4"])

        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_item_up)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.move_up_button)

        self.setLayout(layout)

    def move_item_up(self):
        item_name, ok = QInputDialog.getText(self, "Move Item Up", "Enter the name of the item to move up:")
        if ok:
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).text() == item_name:
                    selected_item = self.list_widget.item(i)
                    index = self.list_widget.row(selected_item)
                    if index > 0:
                        self.list_widget.takeItem(index)
                        self.list_widget.insertItem(0, selected_item.text())
                        self.list_widget.setCurrentRow(0)
                    return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Move Item Up Example")
    window.show()
    sys.exit(app.exec_())
