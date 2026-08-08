"""
Text-to-Speech Service - OpenAI TTS Integration
Generates narration audio for video production.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from openai import AsyncOpenAI, APITimeoutError, APIError

from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.tts")

# Cost per 1M characters (approximate)
TTS_COSTS = {
    "tts-1": 0.015,
    "tts-1-hd": 0.030,
}

VOICE_OPTIONS = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class TTSService:
    """Async text-to-speech using OpenAI TTS."""

    def __init__(self):
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        self._has_api_key = bool(api_key)

        effective_key = api_key or "sk-no-openai-api-key-set"

        self.client = AsyncOpenAI(
            api_key=effective_key,
            timeout=60.0,
            max_retries=2,
        )
        self.output_dir = Path(settings.MOVIES_DIR) / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_available(self) -> bool:
        return self._has_api_key

    async def generate(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0,
        response_format: str = "mp3",
    ) -> Dict[str, Any]:
        """
        Generate speech from text.

        Args:
            text: Text to speak (max 4096 chars)
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            model: Model name (tts-1, tts-1-hd)
            speed: Speaking speed (0.25 - 4.0)
            response_format: mp3, opus, aac, flac, wav, pcm

        Returns:
            Dict with local_path, duration_estimate, cost
        """
        if not self._has_api_key:
            return {
                "local_path": "",
                "error": "api_key_missing",
                "detail": "OPENAI_API_KEY is not configured.",
            }

        if voice not in VOICE_OPTIONS:
            voice = "alloy"

        try:
            logger.info(f"Generating TTS: voice={voice}, model={model}, text_len={len(text)}")

            filename = f"tts_{uuid.uuid4().hex[:8]}.{response_format}"
            filepath = self.output_dir / filename

            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,  # type: ignore
                input=text,
                speed=speed,
                response_format=response_format,  # type: ignore
            )

            # Save audio file
            response.stream_to_file(str(filepath))

            # Estimate cost
            cost = (len(text) / 1_000_000) * TTS_COSTS.get(model, 0.015)

            # Estimate duration (rough: ~150 chars/sec at speed 1.0)
            duration_estimate = (len(text) / 150) / speed

            logger.info(f"TTS saved: {filepath}, est_duration={duration_estimate:.1f}s")

            return {
                "local_path": str(filepath),
                "filename": filename,
                "duration_estimate": round(duration_estimate, 2),
                "cost_usd": round(cost, 6),
                "model": model,
                "voice": voice,
                "text_length": len(text),
            }

        except APITimeoutError as e:
            logger.error(f"TTS timeout: {e}")
            raise
        except APIError as e:
            logger.error(f"TTS API error: {e}")
            raise
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise

    async def generate_ssml(
        self,
        ssml: str,
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Generate speech from SSML.
        Note: OpenAI TTS doesn't support SSML directly, so we strip tags.
        """
        import re
        # Strip SSML tags
        text = re.sub(r"<[^>]+>", "", ssml)
        text = text.strip()
        return await self.generate(text, voice, model, speed)

    def get_voice_for_language(self, language: str) -> str:
        """Get recommended voice for language."""
        voice_map = {
            "th": "alloy",      # Thai - alloy works well
            "en": "nova",       # English - nova is clear
            "ja": "shimmer",    # Japanese
            "zh": "echo",       # Chinese
            "ko": "fable",      # Korean
        }
        return voice_map.get(language, "alloy")


# Global instance
tts_service = TTSService()
