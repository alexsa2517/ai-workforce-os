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
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )
        self.model = settings.OPENAI_MODEL

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
            return {"content": "Error: Request timed out", "usage": {}, "error": "timeout"}
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"content": f"Error: {str(e)}", "usage": {}, "error": "api_error"}
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}", exc_info=True)
            return {"content": f"Error: {str(e)}", "usage": {}, "error": "unexpected"}
