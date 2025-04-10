import openai
import pyperclip
import keyboard
import time

# Set up OpenAI API key
OPENAI_API_KEY = "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"  # Replace with your actual API key
openai.api_key = OPENAI_API_KEY

def query_chatgpt(prompt):
    """Send a prompt to ChatGPT and receive a response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,  # Adjust based on your needs
            temperature=0.7  # Controls creativity
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

def type_response(response):
    """Simulate typing the response."""
    for char in response:
        keyboard.write(char)
        time.sleep(0.01)  # Simulate typing speed

def process_clipboard():
    """Fetch text from clipboard, send it to ChatGPT, and type the response."""
    prompt = pyperclip.paste()
    if prompt:
        print("Sending clipboard text to ChatGPT...")
        response = query_chatgpt(prompt)
        print("Response received. Typing back...")
        type_response(response)
    else:
        print("Clipboard is empty.")

# Set up hotkey listener
keyboard.add_hotkey("ctrl+alt+s", process_clipboard)

print("Script running. Press Ctrl+Alt+S to send clipboard text to ChatGPT.")
keyboard.wait("esc")  # Keeps the script running until you press Esc