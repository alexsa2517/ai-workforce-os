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
        
        # Note: Using legacy google-generativeai for now as per current requirements.txt
        # If switching to google-genai, this would need a major refactor.
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

            # Handle system prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            logger.info(f"Gemini request: model={model or self.model_name}")
            response = current_model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )
            
            # Check for blocked response or empty candidates
            if not response or not response.candidates:
                logger.warning("Gemini API returned no candidates (possibly blocked by safety filters)")
                return {
                    "content": "",
                    "usage": {},
                    "error": "blocked_or_empty",
                    "detail": "Gemini API returned no candidates. This may be due to safety filters.",
                }

            # Safely access text (can raise ValueError if response is blocked)
            try:
                content = response.text
            except ValueError as ve:
                logger.error(f"Could not access Gemini response text: {ve}")
                return {
                    "content": "",
                    "usage": {},
                    "error": "safety_block",
                    "detail": f"Could not access response text: {str(ve)}",
                }
            
            # Gemini provides token count in usage_metadata if available
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            else:
                usage = {"total_tokens": len(content.split()) * 4}
                
            logger.info(f"Gemini response received: {usage.get('total_tokens', '?')} tokens used")
            return {"content": content, "usage": usage}
            
        except Exception as e:
            logger.error(f"Gemini error: {e}", exc_info=True)
            return {
                "content": "",
                "usage": {},
                "error": "api_error",
                "detail": str(e)
            }
