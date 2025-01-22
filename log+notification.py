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

notification_delay = 0.5
number_delay = 3    

def query_chatgpt(prompt):
    """Send a prompt to ChatGPT and receive a response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-4" if you have access
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,  # Adjust based on your needs
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

# Set up hotkey listeners
keyboard.add_hotkey("ctrl+alt+s", process_clipboard)  # First hotkey
keyboard.add_hotkey("ctrl+alt+a", process_question_with_notifications)  # Second hotkey

print("Script running. Use the following hotkeys:")
print(" - Ctrl+Alt+S: Send clipboard text to ChatGPT and type back the response (no notification).")
print(" - Ctrl+Alt+A: Ask ChatGPT to identify the correct numbers and send notifications.")
print("Press Esc to quit.")
keyboard.wait("esc")  # Keeps the script running until you press Esc
