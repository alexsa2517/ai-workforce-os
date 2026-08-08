"""
DeepSeek Async LLM Client
Supports DeepSeek V4 models with OpenAI-compatible API.
"""
import os
import logging
from typing import Any, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI, APITimeoutError, APIError, AuthenticationError
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.deepseek")

# Legacy model mapping
LEGACY_MODEL_MAP = {
    "deepseek-chat": "deepseek-v4-flash",
    "deepseek-reasoner": "deepseek-v4-pro",
}

# Cost per 1K tokens (approximate)
COST_PER_1K = {
    "deepseek-v4-flash": {"input": 0.0001, "output": 0.0001},
    "deepseek-v4-pro": {"input": 0.002, "output": 0.002},
}


class DeepSeekClient:
    """Async DeepSeek client via OpenAI-compatible API."""

    def __init__(self):
        api_key = settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY", "")
        self._has_api_key = bool(api_key)

        base_url = settings.DEEPSEEK_BASE_URL
        effective_key = api_key or "sk-no-deepseek-api-key-set"

        self.client = AsyncOpenAI(
            api_key=effective_key,
            base_url=base_url,
            timeout=settings.LLM_TIMEOUT,
            max_retries=0,
        )
        self.model = settings.DEEPSEEK_MODEL
        self.provider = "deepseek"

    @property
    def is_available(self) -> bool:
        return self._has_api_key

    def _resolve_model(self, model: Optional[str] = None) -> str:
        """Resolve model name, converting legacy names."""
        resolved = model or self.model
        if resolved in LEGACY_MODEL_MAP:
            new_name = LEGACY_MODEL_MAP[resolved]
            logger.info(f"Legacy model '{resolved}' mapped to '{new_name}'")
            return new_name
        return resolved

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        if not self._has_api_key:
            return {
                "content": "",
                "usage": {},
                "error": "api_key_missing",
                "detail": "DEEPSEEK_API_KEY is not configured.",
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resolved_model = self._resolve_model(model)

        try:
            logger.info(f"DeepSeek request: model={resolved_model}")
            response = await self.client.chat.completions.create(
                model=resolved_model,
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

            cost = self._calculate_cost(resolved_model, usage_dict)

            return {
                "content": content,
                "usage": usage_dict,
                "cost_usd": cost,
                "model": response.model,
                "provider": self.provider,
            }

        except AuthenticationError as e:
            logger.error(f"DeepSeek authentication error: {e}")
            raise
        except APITimeoutError as e:
            logger.error(f"DeepSeek timeout: {e}")
            raise
        except APIError as e:
            logger.error(f"DeepSeek API error: {e}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek unexpected error: {e}")
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

        resolved_model = self._resolve_model(model)

        try:
            stream = await self.client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"DeepSeek streaming error: {e}")
            raise

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        rates = COST_PER_1K.get(model, {"input": 0.0001, "output": 0.0001})
        input_cost = (usage.get("prompt_tokens", 0) / 1000) * rates["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1000) * rates["output"]
        return round(input_cost + output_cost, 6)
