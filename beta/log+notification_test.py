import openai
import pyperclip
import keyboard
import time
import requests

# Set up OpenAI API key
OPENAI_API_KEY = "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"  # Replace with your actual API key
openai.api_key = OPENAI_API_KEY

# Pushover API details
user_key = "uyboyw61am8bhvchius7efswdcsd48"
api_token = "ajf2vh6aeouiowpiknbeccuwi1uemd"

# Adjustable delays in seconds
notification_delay = 0.2  # Delay between individual notifications
number_delay = 5  # Delay between sending notifications for different answer numbers

def query_chatgpt(prompt):
    """Simulate a prompt to ChatGPT and return a predefined test response with single or multiple numbers."""
    return "2,1"  # For testing, we use fixed numbers (e.g., 3, 2, 1)

def send_push_notification(title, message):
    """Send a push notification using Pushover."""
    try:
        push_message = {
            "token": api_token,
            "user": user_key,
            "title": title,
            "message": message,
        }
        response = requests.post("https://api.pushover.net/1/messages.json", data=push_message)
        print("Push notification sent:", response.json())
    except Exception as e:
        print(f"Error sending push notification: {e}")

def process_clipboard():
    """Fetch text from clipboard and type a simulated response from ChatGPT."""
    prompt = pyperclip.paste()
    if prompt:
        print("Simulating response for clipboard text...")
        response = query_chatgpt(prompt)
        print("Response received. Typing back...")
        for char in response:
            keyboard.write(char)
            time.sleep(0.01)  # Simulate typing speed
    else:
        print("Clipboard is empty.")

def process_question_with_notifications():
    """Simulate asking ChatGPT to identify the correct numbers in the question and send notifications."""
    prompt = pyperclip.paste()
    if prompt:
        print("Simulating ChatGPT processing question...")
        response = query_chatgpt(prompt)

        print("Response received:", response)

        # Simulate notification sending
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


# Set up hotkey listeners
keyboard.add_hotkey("ctrl+alt+s", process_clipboard)  # First hotkey
keyboard.add_hotkey("ctrl+alt+a", process_question_with_notifications)  # Second hotkey


print("Script running. Use the following hotkeys:")
print(" - Ctrl+Alt+S: Send clipboard text to ChatGPT and type back a simulated response (no token usage).")
print(" - Ctrl+Alt+A: Simulate asking ChatGPT to identify the correct numbers and send notifications.")
print("Press Esc to quit.")
keyboard.wait("esc")  # Keeps the script running until you press Esc
