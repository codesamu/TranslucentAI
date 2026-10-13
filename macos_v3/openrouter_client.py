"""Dependency-light OpenRouter client used by the macOS v3 app and tests."""

from __future__ import annotations

import json
import re
from urllib import error, request


DEFAULT_FREE_MODELS = (
    # OpenRouter maintains this router as free models change over time.
    "openrouter/free",
    # Current catalog fallbacks, also listed as $0 prompt/$0 completion.
    "inclusionai/ling-3.1-flash",
    "apodex/apodex-1.1-mini:free",
)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def answer_numbers(text: str) -> list[str]:
    """Return 1-based answer numbers from numeric or lettered model output.

    For example, ``B`` and ``B. Yellow`` both become ``["2"]``.
    """
    response = text or ""
    numbers = re.findall(r"\b\d+\b", response)
    if numbers:
        return numbers

    # Match standalone option letters, not letters inside ordinary words.
    letters = re.findall(r"(?<![A-Za-z])([A-H])(?![A-Za-z])", response.upper())
    return [str(ord(letter) - ord("A") + 1) for letter in letters]


class OpenRouterClient:
    def __init__(self, api_key: str, models=None, timeout: int = 45):
        self.api_key = api_key.strip()
        self.models = tuple(models or DEFAULT_FREE_MODELS)
        self.timeout = timeout

    def chat(self, prompt: str, *, max_tokens: int = 800) -> str:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        if not self.models:
            raise RuntimeError("No OpenRouter models are configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/codesamu/TranslucentAI",
            "X-Title": "TranslucentAI macOS v3",
        }
        failures = []
        for model in self.models:
            body = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": max_tokens,
            }).encode("utf-8")
            try:
                req = request.Request(OPENROUTER_URL, data=body, headers=headers, method="POST")
                with request.urlopen(req, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"].strip()
                if content:
                    return content
                failures.append(f"{model}: empty response")
            except (error.HTTPError, error.URLError, KeyError, IndexError, TypeError, ValueError) as exc:
                failures.append(f"{model}: {exc}")
        raise RuntimeError("All OpenRouter free models failed: " + "; ".join(failures))
