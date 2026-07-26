"""
Voice Router - API endpoints for text-to-speech and voice services
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

logger = logging.getLogger("ai_workforce.routers.voice")

router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])


@router.post("/tts")
async def text_to_speech(text: str, voice: Optional[str] = "alloy", model: Optional[str] = "tts-1"):
    """
    Convert text to speech audio.

    Args:
        text: Text to convert to speech
        voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
        model: TTS model to use

    Returns:
        Audio file or audio URL
    """
    try:
        from app.services.voice_service import VoiceService

        voice_service = VoiceService()
        result = voice_service.generate_speech(text, voice=voice, model=model)
        return result
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/voices")
async def list_voices():
    """List available voice options."""
    return {
        "voices": [
            {"name": "alloy", "description": "Balanced, neutral voice"},
            {"name": "echo", "description": "Deep, resonant voice"},
            {"name": "fable", "description": "Warm, storytelling voice"},
            {"name": "onyx", "description": "Strong, authoritative voice"},
            {"name": "nova", "description": "Bright, energetic voice"},
            {"name": "shimmer", "description": "Light, youthful voice"},
        ]
    }
