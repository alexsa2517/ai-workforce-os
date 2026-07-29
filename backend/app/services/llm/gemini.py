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
        if not api_key:
            logger.warning("GOOGLE_API_KEY is not set. Gemini API calls will fail.")
        
        genai.configure(api_key=api_key or "no-google-api-key-set")
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
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
        if not self._has_api_key:
            return {
                "content": "",
                "usage": {},
                "error": "api_key_missing",
                "detail": "GOOGLE_API_KEY is not configured. Please set it in .env or environment variables.",
            }

        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            # If a different model is requested, create a temporary model instance
            current_model = self.model
            if model and model != self.model_name:
                current_model = genai.GenerativeModel(model)

            if system_prompt:
                # Gemini support system instructions in the model constructor or prepended
                # Using prepend for compatibility with simple generation call
                prompt = f"{system_prompt}\n\n{prompt}"

            response = current_model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            if not response.text:
                return {"content": "", "usage": {}, "error": "empty_response"}

            content = response.text
            # Gemini provides token count in usage_metadata if available
            usage = {}
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                }
            else:
                usage = {"total_tokens": len(content.split()) * 4}
                
            return {"content": content, "usage": usage}
        except Exception as e:
            logger.error(f"Gemini error: {e}", exc_info=True)
            return {
                "content": "",
                "usage": {},
                "error": "api_error",
                "detail": str(e)
            }
