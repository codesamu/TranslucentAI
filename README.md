<h1 align="center" id="title">👥 TranslucentAI</h1>

<p align="center" id="description"><em>A lightweight Python script to cheat in exams without loosing focus.</em></p>

---

## 🛠️ Usage

Copy the question and use hotkeys to get answers in the following ways:

- **Simulate Keystrokes**: Automatically type the answer.
- **Send Answers to Your Phone**: Get multiple-choice question numbers sent via Pushover notifications.
- **Translucent Window**: Display the answer in a semi-transparent window.
- **Focus**: The code is written in a way that it cant be detected by loosing focus in the window

---

## ⚙️ How It Works

- **Clipboard Integration**: The script grabs the copied question directly from your clipboard.
- **OpenAI GPT-4 API**: Sends the question as a prompt to GPT-4 to generate the answer.
- **PyQt5**: Provides the translucent window functionality.
- **Pushover**: Sends notifications with answers to your phone.

> **Note**: This script won't work with exam software that blocks background processes (e.g., Safe Exam Browser).

### Requirements

1. OpenAI API Key.
2. A Pushover account with your User/API key.
3. Python 3.7 or higher

### Installation

To install all required packages, run:

```bash
pip install -r requirements.txt
```

---

## 🎥 Demo

### Translucent Window Features:

- **Customizable Text Color**: Easily adjust the text color in the code. Default is optimized for Letto.
- **Low Visibility**: Text appears as a faint white shade, making it harder to detect.


<div align="center">
  <img src="https://i.imgur.com/ovhsOTK.jpeg" alt="TranslucentAI Demo 1" width="80%">
  <p>Letto example</p>
  <br>
  <img src="https://i.imgur.com/34mrDto.jpeg" alt="TranslucentAI Demo 2" width="80%">
  <p>Black background for better visibility of the program</p>
</div>

---

## 📦Packages

```bash
pip install pyqt5
```
```bash
pip install openai==0.28
```
```bash
pip install keyboard
```
```bash
pip install requests
```
```bash
pip install threading
```
```bash
pip install pyperclip
```

---

## 🚨 Disclaimer

This script is intended for educational purposes only. Misusing it may have serious consequences.
