"""Kimi / Moonshot AI client using its OpenAI-compatible API."""
import os
from typing import Any, Dict, Optional
from openai import OpenAI
from app.core.config import settings


class KimiClient:
    def __init__(self):
        api_key = settings.KIMI_API_KEY or os.getenv("KIMI_API_KEY", "")
        self._has_api_key = bool(api_key)
        self.client = OpenAI(
            api_key=api_key or "sk-no-kimi-api-key-set",
            base_url=settings.KIMI_BASE_URL,
            timeout=60.0,
            max_retries=2,
        )
        self.model = settings.KIMI_MODEL

    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.4,
                 max_tokens: int = 4096, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self._has_api_key:
            return {"content": "", "usage": {}, "error": "api_key_missing",
                    "detail": "KIMI_API_KEY is not configured."}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            usage = response.usage
            return {
                "content": response.choices[0].message.content or "",
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0),
                },
            }
        except Exception as exc:
            return {"content": "", "usage": {}, "error": "api_error", "detail": str(exc)}
