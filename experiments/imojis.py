import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QPushButton, QGridLayout, QWidget, QLabel, QVBoxLayout, QApplication


class EmojiWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Emoji")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        emojis = ["😀", "😂", "😊", "😎", "😍", "😜", "🤔", "😴", "💪", "👍", "👌", "😱"]  # https://tools.picsart.com/text/emojis/
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
            self.parent().add_selected_emoji(emoji)
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

    def add_selected_emoji(self, emoji):
        self.label.setText(self.label.text() + emoji)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = LabelWindow()
    main_window.show()
    sys.exit(app.exec_())
