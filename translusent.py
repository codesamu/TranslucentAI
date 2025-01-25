from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
import sys

class TransparentWindow(QMainWindow):
    def __init__(self, x=100, y=100, text_color="#FFFFFF"):
        super().__init__()
        self.setWindowTitle("Transparent Window")
        self.setGeometry(x, y, 400, 300)  # Set size
        self.move(x, y)  # Set position on screen

        # Set the window transparency
        self.setWindowOpacity(0.8)

        # Remove the title bar and make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Enable translucent background
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Add a label with text
        label = QLabel("Hello, PyQt!", self)
        label.setStyleSheet(f"font-size: 24px; color: {text_color}; background: transparent;")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
        

    def showEvent(self, event):
        # Prevent the window from taking focus when shown
        self.setWindowFlags(self.windowFlags() | Qt.WindowDoesNotAcceptFocus)
        self.show()

    def keyPressEvent(self, event):
        # Close the window when the Escape key is pressed
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the starting position and text color directly in the code
    START_X = 50  # X position
    START_Y = 900  # Y position
    TEXT_COLOR = "#eeeeee"  # Hex color code for the text (e.g., orange-red)

    window = TransparentWindow(START_X, START_Y, TEXT_COLOR)
    window.show()
    sys.exit(app.exec_())
