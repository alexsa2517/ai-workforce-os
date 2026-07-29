"""
DeepSeek LLM Client - Chat completions with error handling and timeout.

Supports DeepSeek V4 models (deepseek-v4-flash, deepseek-v4-pro).
Note: Legacy model names (deepseek-chat, deepseek-reasoner) were deprecated on 2026-07-24.
Uses OpenAI-compatible API at https://api.deepseek.com
"""
import os
import logging
from typing import Any, Dict, Optional
from openai import OpenAI, APITimeoutError, APIError
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.deepseek")

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3

# Legacy model name mapping (deprecated 2026-07-24)
LEGACY_MODEL_MAP = {
    "deepseek-chat": "deepseek-v4-flash",
    "deepseek-reasoner": "deepseek-v4-pro",
}


class DeepSeekClient:
    """DeepSeek chat completions client via OpenAI-compatible API."""

    def __init__(self):
        api_key = settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            logger.warning(
                "DEEPSEEK_API_KEY is not set. DeepSeek API calls will fail. "
                "Set DEEPSEEK_API_KEY in .env or environment variables."
            )

        base_url = getattr(settings, "DEEPSEEK_BASE_URL", None) or os.getenv(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        )

        # Use a placeholder key if not set (prevents OpenAI client init error)
        # The actual API call will fail gracefully with a clear error message
        effective_key = api_key or "sk-no-deepseek-api-key-set"

        self.client = OpenAI(
            api_key=effective_key,
            base_url=base_url,
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )
        self.model = settings.DEEPSEEK_MODEL
        self._has_api_key = bool(api_key)

    def _resolve_model(self, model: Optional[str] = None) -> str:
        """Resolve model name, converting legacy names to V4 equivalents."""
        resolved = model or self.model
        if resolved in LEGACY_MODEL_MAP:
            new_name = LEGACY_MODEL_MAP[resolved]
            logger.info(f"Legacy model '{resolved}' mapped to '{new_name}'")
            return new_name
        return resolved

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion via DeepSeek API.

        Args:
            prompt: User message
            model: Override model name (supports deepseek-v4-flash, deepseek-v4-pro)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dict with 'content' and 'usage' keys
        """
        resolved_model = self._resolve_model(model)

        # Validate API key before making the request
        if not self._has_api_key:
            return {
                "content": "",
                "usage": {},
                "error": "api_key_missing",
                "detail": "DEEPSEEK_API_KEY is not configured. Please set it in .env or environment variables. Get your key at https://platform.deepseek.com/",
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.info(
                f"DeepSeek request: model={resolved_model}, "
                f"max_tokens={max_tokens}, temperature={temperature}"
            )
            response = self.client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            logger.info(
                f"DeepSeek response: {usage.get('total_tokens', '?')} tokens used"
            )
            return {"content": content, "usage": usage}
        except APITimeoutError as e:
            logger.error(f"DeepSeek timeout: {e}")
            return {
                "content": "",
                "usage": {},
                "error": "timeout",
                "detail": "Request to DeepSeek API timed out. Please try again.",
            }
        except APIError as e:
            logger.error(f"DeepSeek API error: {e}")
            return {
                "content": "",
                "usage": {},
                "error": "api_error",
                "detail": str(e),
            }
        except Exception as e:
            logger.error(f"DeepSeek unexpected error: {e}", exc_info=True)
            return {
                "content": "",
                "usage": {},
                "error": "unexpected",
                "detail": str(e),
            }

    def list_models(self) -> Dict[str, Any]:
        """List available DeepSeek models."""
        return {
            "models": [
                {"id": "deepseek-v4-flash", "description": "Efficiency-optimized, 284B MoE, 13B active params"},
                {"id": "deepseek-v4-pro", "description": "Full capability model with 1.6T parameters"},
            ],
            "deprecated": [
                {"id": "deepseek-chat", "replacement": "deepseek-v4-flash", "deprecated_on": "2026-07-24"},
                {"id": "deepseek-reasoner", "replacement": "deepseek-v4-pro", "deprecated_on": "2026-07-24"},
            ],
        }
