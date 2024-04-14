import sys
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import time
import threading
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
