<h1 align="center" id="title">TranslucentAI</h1>

<p id="description">A lightweight python script to cheat in exams</p>
 
 
<h2>Usage</h2>
<p><p>

copy the question and press a hotkey to get the answer in these ways . . .

*   hotkey to simulate keystrokes with the answer
*   hotkey to get the multiple choice question answer numbers sent to your phone
*   hotkey to get the multiple choice question answer shown on a translucent window

<p><p>

<h2>How it works</h2>
<p><p>
it gets the copied question from the clipboard and sends the prompt to gpt4. The python script uses PyQt5 for the translucent window and pushover to send the notifications to your phone. The only downside is that if a exam program blocks any background activity like "safe exam browser" it cant get the question from the clipboard.

For it to work you need  a openAI API key and a Pushover account with user/api key!

<h2>Demo</h2>
<p><p>
translucent window:

* text colour can be changed in the code. Default color is for Letto
* the text is a slightly darker white to be hard to be detected
<p><p>
<img src="https://i.imgur.com/ovhsOTK.jpeg" alt="project-screenshot" width="1920" height="500/">
<img src="https://i.imgur.com/34mrDto.jpeg" alt="project-screenshot" width="1920" height="500/">

