import pyperclip
import keyboard
import time

# Predefined response string
PREDEFINED_RESPONSE = "This is a test response to save API tokens"

def type_response(response):
    """Simulate typing the response."""
    time.sleep(1.5)
    for char in response:
        keyboard.write(char)
        time.sleep(0.01)  # Simulate typing speed

def process_clipboard():
    """Fetch text from clipboard and type the predefined response."""
    prompt = pyperclip.paste()
    if prompt:
        print("Clipboard text detected. Typing predefined response...")
        type_response(PREDEFINED_RESPONSE)
    else:
        print("Clipboard is empty.")

# Set up hotkey listener
keyboard.add_hotkey("ctrl+alt+s", process_clipboard)

print("Script running. Press Ctrl+Alt+S to type the predefined response.")
keyboard.wait("esc")  # Keeps the script running until you press Esc
