/**
 * Background script for Stealth Mode
 */
chrome.commands.onCommand.addListener(async (command) => {
  if (command === "_execute_sidebar_action" || command === "stealth-analyze") {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;

    // 1. Get API Key
    const { openrouter_api_key } = await chrome.storage.local.get(['openrouter_api_key']);
    if (!openrouter_api_key) {
      console.error("No API Key found");
      return;
    }

    // 2. Get Content from Tab
    chrome.tabs.sendMessage(tab.id, { action: "getContent" }, async (response) => {
      if (!response || !response.content) return;

      // 3. Call OpenRouter
      try {
        const answer = await callOpenRouter(openrouter_api_key, response.content);
        // 4. Send Answer back for injection
        chrome.tabs.sendMessage(tab.id, { action: "injectAnswer", answer: answer });
      } catch (e) {
        console.error("Stealth Analysis failed", e);
        chrome.tabs.sendMessage(tab.id, { action: "error" });
      }
    });
  }
});

async function callOpenRouter(apiKey, content) {
  // Use the fallback models list
  const models = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-next-80b-a3b-instruct:free"
  ];

  for (const model of models) {
    try {
      const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${apiKey}`,
          "Content-Type": "application/json",
          "HTTP-Referer": "http://localhost",
          "X-Title": "Stealth Analyzer"
        },
        body: JSON.stringify({
          "model": model,
          "messages": [{
            "role": "user",
            "content": `Analyze MCQ. Output ONLY the correct indices/numbers. Separate with commas if multiple. No other text.\n\nContent:\n${content}`
          }],
          "temperature": 0.1
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.choices[0].message.content;
      }
    } catch (e) {
      continue;
    }
  }
  throw new Error("All models failed");
}
