/**
 * Content script to extract visible text from the page.
 */
function extractPageContent() {
  // Extract text while preserving some structure with newlines
  const content = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  let node;
  while(node = walk.nextNode()) {
    const parent = node.parentElement;
    if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE' || parent.tagName === 'NAV' || parent.tagName === 'FOOTER') continue;
    
    const text = node.textContent.trim();
    if (text) {
      content.push(text);
    }
  }
  
  // Join with newlines and limit
  return content.join('\n').substring(0, 6000);
}

// Status dot for stealth feedback
function updateStatus(color) {
  let dot = document.getElementById('translucent-status-dot');
  if (!dot) {
    dot = document.createElement('div');
    dot.id = 'translucent-status-dot';
    dot.style.cssText = 'position:fixed;top:2px;left:2px;width:3px;height:3px;border-radius:50%;z-index:999999;pointer-events:none;';
    document.body.appendChild(dot);
  }
  dot.style.backgroundColor = color;
  if (color === 'transparent') return;
  setTimeout(() => dot.style.backgroundColor = 'transparent', 3000);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getContent") {
    updateStatus('yellow');
    const content = extractPageContent();
    sendResponse({ content: content });
  } else if (request.action === "injectAnswer") {
    updateStatus('green');
    injectStealthAnswer(request.answer);
  } else if (request.action === "error") {
    updateStatus('red');
  }
  return true;
});

function injectStealthAnswer(answer) {
  // 1. Remove any old answers first
  const oldAnswers = document.querySelectorAll('.translucent-answer');
  oldAnswers.forEach(el => el.remove());

  const elements = document.querySelectorAll('p, span, h1, h2, h3, div, b, i');
  let target = null;
  const keywords = ['Punkt(e)', 'Beispiel', 'Frage', 'Pkt', 'SPS'];
  
  for (const el of elements) {
    if (keywords.some(k => el.textContent.includes(k))) {
      target = el;
      break;
    }
  }

  if (!target) target = document.querySelector('h1') || document.body;

  const stealthEl = document.createElement('span');
  stealthEl.className = 'translucent-answer'; // Class for easy cleanup
  stealthEl.textContent = ` [${answer}]`;
  stealthEl.style.cssText = `
    font-size: 11px !important;
    opacity: 0.4 !important;
    color: #2575fc !important;
    font-weight: bold !important;
    margin-left: 8px !important;
    display: inline !important;
  `;
  
  target.appendChild(stealthEl);
}
