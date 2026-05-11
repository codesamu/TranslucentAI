<h1 align="center" id="title">👥 TranslucentAI</h1>

<p align="center" id="description"><em>An invisible AI assistant for web pages and exams, featuring a browser extension and a desktop script.</em></p>

---

## 🚀 Two Powerful Tools

TranslucentAI comes in two flavors depending on your needs:

1. **Browser Extension (Main Feature)**: Seamlessly analyze web pages right from your browser using OpenRouter's free AI models.
2. **Desktop Script (PyQt)**: A lightweight Python script to get answers via hotkeys without losing window focus.

---

## 🧩 1. Browser Extension (Main)

A stealthy Firefox extension that analyzes multiple-choice questions on web pages and returns the correct answers in a compact, unobtrusive UI.

### ✨ Features
- **Compact UI**: Designed to be minimal and blend into white pages so it's less easy to spot.
- **OpenRouter Integration**: Uses powerful open-source models (e.g., Llama 3) for free.
- **Stealth Mode**: Designed to be as invisible as possible during usage.

### 🛠️ Installation
1. Clone this repository.
2. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`.
3. Click **Load Temporary Add-on...**
4. Select the `manifest.json` file inside the `openrouter-extension` folder.

### ⚙️ Usage
1. Click the extension icon.
2. Enter your OpenRouter API Key.
3. Click **Analyze** to automatically grab page content and get the correct answers.

---

## 💻 2. Desktop Script (PyQt)

A background Python script that monitors your clipboard. Copy a question, press a hotkey, and get the answer displayed in a translucent, nearly invisible window or sent to your phone.

### ✨ Features
- **Simulate Keystrokes**: Automatically type the answer.
- **Translucent Window (PyQt5)**: Displays the answer in a faint, semi-transparent window overlay using PyQt.
- **Pushover Support**: Sends answers directly to your phone via notifications.
- **Undetectable Focus**: Designed to avoid triggering "lost focus" alerts in most standard software.

### 🛠️ Installation & Setup
1. Ensure Python 3.7+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your OpenAI API key (or other supported keys):
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### ⚙️ Usage
Run the script from your terminal:
```bash
python TranslucentAI.py
```

> **Note**: This script won't work with exam software that completely blocks background processes (e.g., Safe Exam Browser).

---

## 🚨 Disclaimer

This software is intended for educational and testing purposes only. Misusing it may have serious consequences.
