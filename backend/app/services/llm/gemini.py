"""
Google Gemini LLM Client - Chat completions with error handling
"""
import os
import logging
from typing import Any, Dict, Optional
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.gemini")


class GeminiClient:
    """Google Gemini chat client with error handling."""

    def __init__(self):
        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        genai.configure(api_key=api_key)
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini.

        Args:
            prompt: User message
            model: Override model name
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dict with 'content' and 'usage' keys
        """
        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if system_prompt:
                # Gemini doesn't support system role directly; prepend to user message
                prompt = f"{system_prompt}\n\n{prompt}"

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            content = response.text
            # Gemini doesn't provide detailed token usage in the same way
            usage = {"total_tokens": len(content.split()) * 4}  # rough estimate
            return {"content": content, "usage": usage}
        except Exception as e:
            logger.error(f"Gemini error: {e}", exc_info=True)
            return {"content": f"Error: {str(e)}", "usage": {}, "error": str(e)}
