from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt, QTimer
import sys
import openai
import pyperclip
import keyboard
import time
import requests
import threading

# Set up OpenAI API key
OPENAI_API_KEY = "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"  # Replace with your actual API key
openai.api_key = OPENAI_API_KEY

# Pushover API details
user_key = "uyboyw61am8bhvchius7efswdcsd48"
api_token = "ajf2vh6aeouiowpiknbeccuwi1uemd"

notification_delay = 1
number_delay = 4

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
        self.label = QLabel("text", self)
        self.label.setStyleSheet(f"font-size: 24px; color: {text_color}; background: transparent;")
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

    def showEvent(self, event):
        """Override to handle focus and window display."""
        # Prevent the window from taking focus when shown
        self.setWindowFlags(self.windowFlags() | Qt.WindowDoesNotAcceptFocus)
        self.show()

    def keyPressEvent(self, event):
        """Override to handle the Escape key to close the window."""
        if event.key() == Qt.Key_Escape:
            self.close()

    def update_label(self, text):
        """Update the label text in the window."""
        # Ensure label updates happen on the main UI thread
        self.label.setText(text)
        QApplication.processEvents()  # Force UI update


def query_chatgpt(prompt):
    """Send a prompt to ChatGPT and receive a response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-4" if you have access
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,  # Adjust based on your needs
            temperature=0.7  # Controls creativity
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

def send_push_notification(title, message):
    """Send a push notification using Pushover."""
    try:
        push_message = {
            "token": api_token,
            "user": user_key,
            "title": title,
            "message": message,
            "device": "iphone"
        }
        response = requests.post("https://api.pushover.net/1/messages.json", data=push_message)
        print("Push notification sent:", response.json())
    except Exception as e:
        print(f"Error sending push notification: {e}")

def process_clipboard():
    """Fetch text from clipboard and type the response from ChatGPT."""
    prompt = pyperclip.paste()
    if prompt:
        print("Sending clipboard text to ChatGPT...")
        response = query_chatgpt(prompt)
        print("Response received. Typing back...")
        for char in response:
            keyboard.write(char)
            time.sleep(0.01)  # Simulate typing speed
    else:
        print("Clipboard is empty.")

def process_question_with_notifications():
    """Ask ChatGPT to identify the correct numbers in the question and send notifications."""
    prompt = pyperclip.paste()
    if prompt:
        # Ask ChatGPT to only return the numbers
        question_prompt = (
            f"In the following multiple-choice question, identify only the number(s) of the correct answer: {prompt}. "
            f"Respond with just the number(s), separated by commas if there are multiple."
            f"if number one is right, give back 1. if number 3 then 3."
        )
        print("Sending question to ChatGPT...")
        response = query_chatgpt(question_prompt)

        print("Response received:", response)

        # Extract numbers from the response
        numbers = response.split(",")  # Split numbers by commas
        numbers = [num.strip() for num in numbers if num.strip().isdigit()]  # Clean up and ensure they are digits

        # Send the required number of notifications
        if response:
            numbers = [int(num.strip()) for num in response.split(",") if num.strip().isdigit()]
            for number in numbers:
                for i in range(number):
                    send_push_notification("num", f"{i + 1}/{number}")
                    print(f"num {i + 1}/{number}")
                    time.sleep(notification_delay)  # Delay between individual notifications
                time.sleep(number_delay)  # Delay between different answer numbers
    else:
        print("Clipboard is empty.")

def test_label_update():
    """Test updating the label with a simple string."""
    window.update_label("Hello, World!")
    QApplication.processEvents()  # Force UI update


def process_question_and_show_number():
    """Ask ChatGPT to identify the correct numbers and update the window without sending notifications."""
    def _process():
        prompt = pyperclip.paste()
        if prompt:
            print("Clipboard content:", prompt)  # Debug print
            # Ask ChatGPT to only return the numbers
            question_prompt = (
                f"In the following multiple-choice question, identify only the number(s) of the correct answer: {prompt}. "
                f"Respond with just the number(s), separated by commas if there are multiple."
                f"if number one is right, give back 1. if number 3 then 3."
            )
            print("Sending question to ChatGPT...")  # Debug print
            response = query_chatgpt(question_prompt)

            print("Response received:", response)  # Debug print

            # Extract numbers from the response
            numbers = response.split(",")  # Split numbers by commas
            numbers = [num.strip() for num in numbers if num.strip().isdigit()]  # Clean up and ensure they are digits

            # Update the window label with the right number(s)
            if numbers:
                print("Updating label with numbers:", numbers)  # Debug print
                window.update_label("Correct number(s): " + ", ".join(numbers))
            else:
                print("No correct numbers identified.")  # Debug print
                window.update_label("No correct numbers identified.")
        else:
            print("Clipboard is empty.")  # Debug print
            window.update_label("Clipboard is empty.")

    # Run the function in a separate thread
    threading.Thread(target=_process, daemon=True).start()

def setup_hotkeys():
    """Set up hotkeys for various actions."""
    keyboard.add_hotkey("ctrl+alt+s", process_clipboard)  # First hotkey
    keyboard.add_hotkey("ctrl+alt+a", process_question_with_notifications)  # Second hotkey
    keyboard.add_hotkey("ctrl+alt+d", process_question_and_show_number)  # New hotkey to show the correct number(s) in window
    keyboard.add_hotkey("ctrl+alt+t", test_label_update)  # Test hotkey

def run_event_loop():
    """Ensure the event loop keeps running and doesn't block."""
    while True:
        # Handle any pending events in the QApplication
        QApplication.processEvents()
        time.sleep(0.1)  # Debug print

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the starting position and text color directly in the code
    START_X = 50  # X position
    START_Y = 900  # Y position
    TEXT_COLOR = "#eeeeee"  # Hex color code for the text (e.g., orange-red)

    window = TransparentWindow(START_X, START_Y, TEXT_COLOR)
    window.show()

    setup_hotkeys()
    print("Script running. Use the following hotkeys:")
    print(" - Ctrl+Alt+S: Send clipboard text to ChatGPT and type back the response (no notification).")
    print(" - Ctrl+Alt+A: Ask ChatGPT to identify the correct numbers and send notifications.")
    print(" - Ctrl+Alt+D: Show correct numbers in the transparent window without notifications.")
    print("Press Esc to quit.")

    # Run the event loop for both the app and keyboard listeners
    run_event_loop()

    sys.exit(app.exec_())  # Keep the PyQt5 application running
