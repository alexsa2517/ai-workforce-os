"""
Gemini Media Service
Supports image/video generation via Gemini.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("ai_workforce.llm.gemini_media")


class GeminiMediaService:
    """Gemini media generation service."""

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate media using Gemini."""
        logger.info(f"Gemini media generation requested: {prompt[:50]}...")
        return {"status": "not_implemented", "detail": "Gemini media generation not yet implemented"}
