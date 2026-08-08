"""
Google Gemini Async LLM Client
Handles library loading errors gracefully.
"""
import os
import logging
from typing import Any, Dict, Optional, AsyncGenerator
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.gemini")

# Lazy import
genai = None
_import_error = None

try:
    import google.generativeai as _genai
    genai = _genai
except Exception as e:
    _import_error = str(e)
    logger.warning(f"Gemini library not available: {e}")


class GeminiClient:
    """Async Gemini client with error handling."""

    def __init__(self):
        self._has_api_key = False
        self.model = None
        self.model_name = settings.GEMINI_MODEL
        self.provider = "gemini"

        if _import_error:
            logger.warning(f"GeminiClient in restricted mode: {_import_error}")
            return

        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set")
            return

        if genai:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self._has_api_key = True
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")

    @property
    def is_available(self) -> bool:
        return self._has_api_key and genai is not None

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate content using Gemini."""
        if _import_error:
            return {
                "content": "",
                "usage": {},
                "error": "library_blocked",
                "detail": f"Gemini library unavailable: {_import_error}",
            }

        if not self._has_api_key:
            return {
                "content": "",
                "usage": {},
                "error": "api_key_missing",
                "detail": "GOOGLE_API_KEY is not configured.",
            }

        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            model_instance = self.model
            if model and model != self.model_name:
                model_instance = genai.GenerativeModel(model)

            response = await model_instance.generate_content_async(
                prompt,
                generation_config=generation_config,
            )

            content = response.text if hasattr(response, "text") else ""

            # Estimate usage (Gemini doesn't always return token counts)
            estimated_input = len(prompt.split())
            estimated_output = len(content.split())
            usage_dict = {
                "prompt_tokens": estimated_input,
                "completion_tokens": estimated_output,
                "total_tokens": estimated_input + estimated_output,
                "estimated": True,
            }

            return {
                "content": content,
                "usage": usage_dict,
                "cost_usd": 0.0,  # Gemini pricing varies, track separately
                "model": model or self.model_name,
                "provider": self.provider,
            }

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
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
        if not self.is_available:
            yield ""
            return

        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            model_instance = self.model
            if model and model != self.model_name:
                model_instance = genai.GenerativeModel(model)

            response = await model_instance.generate_content_async(
                prompt,
                generation_config=generation_config,
                stream=True,
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise
