document.addEventListener('DOMContentLoaded', async () => {
  const apiKeyInput = document.getElementById('apiKey');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const output = document.getElementById('output');
  const resultContainer = document.getElementById('resultContainer');



  // Load saved API key
  const stored = await chrome.storage.local.get(['openrouter_api_key']);
  if (stored.openrouter_api_key) {
    apiKeyInput.value = stored.openrouter_api_key;
  }

  analyzeBtn.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
      alert('Please enter an OpenRouter API key');
      return;
    }

    // Save key
    await chrome.storage.local.get(['openrouter_api_key']).then(async (stored) => {
      if (stored.openrouter_api_key !== apiKey) {
        await chrome.storage.local.set({ openrouter_api_key: apiKey });
      }
    });

    // UI Feedback
    analyzeBtn.disabled = true;
    resultContainer.classList.remove('hidden');
    output.textContent = 'Extracting page content...';
    // UI feedback simplified (no loader or btnText)

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const response = await chrome.tabs.sendMessage(tab.id, { action: "getContent" });
      const pageContent = response.content;

      // Show scraped content in debug field if present
      const debugContainer = document.getElementById('debugContainer');
      const scrapedContentDiv = document.getElementById('scrapedContent');
      if (debugContainer && scrapedContentDiv) {
        debugContainer.classList.remove('hidden');
        scrapedContentDiv.textContent = pageContent || 'No content found.';
      }

      if (!pageContent) throw new Error('Could not extract content.');

      // Try models in sequence (Fallback Logic)
      const models = [
        "openai/gpt-oss-120b:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen3-next-80b-a3b-instruct:free"
      ];

      let aiResponse = "";
      for (const model of models) {
        output.textContent = `Testing model: ${model.split('/')[1]}...`;
        try {
          aiResponse = await callOpenRouter(apiKey, pageContent, model);
          if (aiResponse) break; // Success!
        } catch (e) {
          console.warn(`Model ${model} failed: ${e.message}`);
          output.textContent = `Model ${model.split('/')[1]} failed. Trying fallback...`;
        }
      }

      if (aiResponse) {
        output.textContent = aiResponse;
      } else {
        throw new Error("None of the models worked. Check your API key and limit.");
      }

    } catch (error) {
      output.textContent = `Error: ${error.message}`;
    } finally {
      analyzeBtn.disabled = false;
  
  
    }
  });

  const testBtn = document.getElementById('testBtn');
  testBtn.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) { alert('Enter API Key'); return; }
    resultContainer.classList.remove('hidden');
    output.textContent = 'Testing connection...';
    try {
      const aiResponse = await callOpenRouter(apiKey, "Say 'Connection Successful'", "meta-llama/llama-3.3-70b-instruct:free");
      output.textContent = `Success: ${aiResponse}`;
    } catch (error) {
      output.textContent = `Test Failed: ${error.message}`;
    }
  });
});

async function callOpenRouter(apiKey, content, model) {
  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "http://localhost",
      "X-Title": "Translucent AI Extension"
    },
    body: JSON.stringify({
      "model": model,
      "messages": [
        {
          "role": "user",
          "content": `Instructions: Analyze the following content which contains a multiple-choice or multiple-response question. 
1. Identify all correct answers.
2. Provide ONLY the numbers or indices of the correct answers. 
3. If there are multiple correct answers, separate them with commas (e.g., "3, 6, 7").
4. Do not include any other text or explanation.

Content:
${content}`
        }
      ],
      "temperature": 0.2,
      "max_tokens": 4000
    })
  });

  if (!response.ok) {
    const errData = await response.json();
    throw new Error(errData.error?.message || `Status: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}
