"""Anthropic Claude Messages API adapter."""
import os
from typing import Any, Dict, Optional
import requests
from app.core.config import settings


class ClaudeClient:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = settings.CLAUDE_MODEL
        self.base_url = settings.ANTHROPIC_BASE_URL.rstrip("/")

    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.4,
                 max_tokens: int = 4096, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {"content": "", "usage": {}, "error": "api_key_missing",
                    "detail": "ANTHROPIC_API_KEY is not configured."}
        payload = {
            "model": model or self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
        try:
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json=payload,
                timeout=90,
            )
            response.raise_for_status()
            data = response.json()
            text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
            usage = data.get("usage", {})
            return {"content": text, "usage": {
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            }}
        except Exception as exc:
            return {"content": "", "usage": {}, "error": "api_error", "detail": str(exc)}
