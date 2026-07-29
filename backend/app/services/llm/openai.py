"""
OpenAI LLM Client - Chat completions with error handling and timeout
"""
import os
import logging
from typing import Any, Dict, Optional
from openai import OpenAI, APITimeoutError, APIError
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.openai")

DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 2


class OpenAIClient:
    """OpenAI chat completions client with retry and error handling."""

    def __init__(self):
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set. OpenAI API calls will fail.")
        
        # Use placeholder to prevent init error
        effective_key = api_key or "sk-no-openai-api-key-set"
        
        self.client = OpenAI(
            api_key=effective_key,
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )
        self.model = settings.OPENAI_MODEL
        self._has_api_key = bool(api_key)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion.

        Args:
            prompt: User message
            model: Override model name
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dict with 'content' and 'usage' keys
        """
        if not self._has_api_key:
            return {
                "content": "",
                "usage": {},
                "error": "api_key_missing",
                "detail": "OPENAI_API_KEY is not configured. Please set it in .env or environment variables.",
            }

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
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            return {"content": content, "usage": usage}
        except APITimeoutError as e:
            logger.error(f"OpenAI timeout: {e}")
            return {
                "content": "",
                "usage": {},
                "error": "timeout",
                "detail": "Request to OpenAI API timed out.",
            }
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "content": "",
                "usage": {},
                "error": "api_error",
                "detail": str(e),
            }
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}", exc_info=True)
            return {
                "content": "",
                "usage": {},
                "error": "unexpected",
                "detail": str(e),
            }
