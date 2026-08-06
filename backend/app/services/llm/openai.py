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
            logger.info(f"OpenAI request: model={model or self.model}, max_tokens={max_tokens}")
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Check for error in response (some proxies return error field instead of raising)
            if hasattr(response, 'error') and response.error:
                logger.error(f"OpenAI API returned an error: {response.error}")
                return {
                    "content": "",
                    "usage": {},
                    "error": "api_error",
                    "detail": str(response.error),
                }

            if not response or not hasattr(response, 'choices') or not response.choices:
                logger.error("OpenAI API returned an empty or invalid response")
                return {
                    "content": "",
                    "usage": {},
                    "error": "empty_response",
                    "detail": "OpenAI API returned an empty or invalid response.",
                }

            choice = response.choices[0]
            content = choice.message.content if hasattr(choice, 'message') else ""
            
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0),
                }
            
            logger.info(f"OpenAI response received: {usage.get('total_tokens', '?')} tokens used")
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
