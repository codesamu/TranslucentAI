from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt, QTimer
import sys
import openai
import pyperclip
import keyboard
import time
import threading

OPENAI_API_KEY = "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"  # Replace with your actual API key
openai.api_key = OPENAI_API_KEY

class TransparentWindow(QMainWindow):
    def __init__(self, x=100, y=100, text_color="#FFFFFF"):
        super().__init__()
        self.setWindowTitle("Transparent Window")
        self.setGeometry(x, y, 400, 300)
        self.move(x, y)
        self.setWindowOpacity(0.8)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel("AI", self)
        self.label.setStyleSheet(f"font-size: 24px; color: {text_color}; background: transparent;")
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

    def showEvent(self, event):
        """Override to handle focus and window display."""
        self.setWindowFlags(self.windowFlags() | Qt.WindowDoesNotAcceptFocus)
        self.show()

    def keyPressEvent(self, event):
        """Override to handle the Escape key to close the window."""
        if event.key() == Qt.Key_Escape:
            self.close()

    def update_label(self, text):
        """Update the label text in the window."""
        self.label.setText(text)
        QApplication.processEvents()

def query_chatgpt(prompt):
    """Send a prompt to ChatGPT and receive a response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7  # Controls creativity
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"
    
def process_clipboard():
    """Fetch text from clipboard and type the response from ChatGPT."""
    prompt = pyperclip.paste()
    if prompt:
        print("sending...")
        response = query_chatgpt(prompt)
        print("received")
        for char in response:
            keyboard.write(char)
            time.sleep(0.01)
    else:
        print("clipboard is empty.")


def process_question_and_show_number():
    """Ask ChatGPT to identify the correct numbers and update the window without sending notifications."""
    def _process():
        prompt = pyperclip.paste()
        if prompt:
            question_prompt = (
                f"In the following multiple-choice question, identify only the number(s) of the correct answer: {prompt}. "
                f"Respond with just the number(s), separated by commas if there are multiple."
            )
            print("sending...")
            response = query_chatgpt(question_prompt)
            print("received: ", response)

            numbers = response.split(",")
            numbers = [num.strip() for num in numbers if num.strip().isdigit()]

            if numbers:
                window.update_label("" + ", ".join(numbers))
            else:
                print("error: no numbers were given")
                window.update_label("error")
        else:
            print("Clipboard is empty.")
            window.update_label("Clipboard is empty.")

    threading.Thread(target=_process, daemon=True).start()

def process_question_and_show_answer():
    """Ask ChatGPT to identify the correct numbers and update the window without sending notifications."""
    def _process():
        prompt = pyperclip.paste()
        if prompt:
            question_prompt = (
                f"In the following question, identify only the number of the answer: {prompt}. "
                f"Respond with just the number(s), separated by commas if there are multiple."
            )
            print("sending...")
            response = query_chatgpt(question_prompt)
            print("received: ", response)

            numbers = response.split(",")
            numbers = [num.strip() for num in numbers if num.strip().isdigit()]

            if numbers:
                window.update_label("" + ", ".join(numbers))
            else:
                print("error: no numbers were given")
                window.update_label("error")
        else:
            print("Clipboard is empty.")
            window.update_label("Clipboard is empty.")

    threading.Thread(target=_process, daemon=True).start()

def setup_hotkeys():
    """Set up hotkeys for various actions."""
    keyboard.add_hotkey("ctrl+alt+s", process_clipboard)
    keyboard.add_hotkey("ctrl+alt+d", process_question_and_show_number)
    keyboard.add_hotkey("ctrl+alt+f", process_question_and_show_answer)

def run_event_loop():
    """Ensure the event loop keeps running and doesn't block."""
    while True:
        QApplication.processEvents()
        if keyboard.is_pressed('esc'):
            window.close()
            QApplication.quit()
            sys.exit(0)
            break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    START_X = 50 
    START_Y = 900
    TEXT_COLOR = "#eeeeee"

    window = TransparentWindow(START_X, START_Y, TEXT_COLOR)
    window.show()

    setup_hotkeys()
    print(" - Ctrl+Alt+S: simulate keyboard-strokes")
    print(" - Ctrl+Alt+D: show number on screen")
    print(" - Ctrl+Alt+F: show answer on screen")
    print("esc -> stop")

    run_event_loop()
    sys.exit(app.exec_())