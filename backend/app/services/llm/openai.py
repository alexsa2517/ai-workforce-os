"""
OpenAI Async LLM Client
Supports streaming, async operations, and structured error handling.
"""
import os
import logging
from typing import Any, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI, APITimeoutError, APIError, AuthenticationError
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.openai")

# Cost per 1K tokens (approximate, update as needed)
COST_PER_1K = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
}


class OpenAIClient:
    """Async OpenAI client with retry, streaming, and cost tracking."""

    def __init__(self):
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        self._has_api_key = bool(api_key)

        effective_key = api_key or "sk-no-openai-api-key-set"

        self.client = AsyncOpenAI(
            api_key=effective_key,
            timeout=settings.LLM_TIMEOUT,
            max_retries=0,  # We handle retries at factory level
        )
        self.model = settings.OPENAI_MODEL
        self.provider = "openai"

    @property
    def is_available(self) -> bool:
        return self._has_api_key

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion asynchronously."""
        if not self._has_api_key:
            return {
                "content": "",
                "usage": {},
                "error": "api_key_missing",
                "detail": "OPENAI_API_KEY is not configured.",
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.info(f"OpenAI request: model={model or self.model}")
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content or ""
            usage = response.usage
            usage_dict = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }

            # Calculate cost
            cost = self._calculate_cost(model or self.model, usage_dict)

            return {
                "content": content,
                "usage": usage_dict,
                "cost_usd": cost,
                "model": response.model,
                "provider": self.provider,
            }

        except AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise
        except APITimeoutError as e:
            logger.error(f"OpenAI timeout: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        if not self._has_api_key:
            yield ""
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """Calculate approximate cost in USD."""
        rates = COST_PER_1K.get(model, COST_PER_1K.get("gpt-4o", {"input": 0.005, "output": 0.015}))
        input_cost = (usage.get("prompt_tokens", 0) / 1000) * rates["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1000) * rates["output"]
        return round(input_cost + output_cost, 6)
