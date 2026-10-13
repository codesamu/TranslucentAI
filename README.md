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

The app uses OpenRouter's `openrouter/free` router, which automatically selects
an available free model. You can override it with a comma-separated
`OPENROUTER_MODELS` value in `.env` if needed.

> **Note**: This script won't work with exam software that completely blocks background processes (e.g., Safe Exam Browser).

## 🍎 3. macOS PyQt v3 (OpenRouter Free)

`macos_v3/` is the third desktop version. It keeps the translucent PyQt overlay
from the original version but uses OpenRouter's free models with automatic
fallbacks. Copy `.env.example` to `.env`, add an OpenRouter API key, then run:

```bash
cd macos_v3
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python TranslucentAI.py
```

The overlay starts as a readable dark panel near the top-left of the primary
screen. Left-drag the text or loading circle independently, right-click either
one or press `Ctrl+Alt+M` for settings, and adjust their separate opacity and
exact positions there. Enable
“Show overlay on every macOS Space” if you use multiple workspaces; the
setting is remembered with macOS preferences.

Run its offline tests with `python -m unittest -v test_translucent_ai.py` from
the `macos_v3` directory. The app does not contain API keys; macOS may also
require Accessibility permission for global hotkeys and typing.

---

## 🚨 Disclaimer

This software is intended for educational and testing purposes only. Misusing it may have serious consequences.
