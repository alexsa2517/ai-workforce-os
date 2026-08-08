"""
Voice Router - TTS endpoints
"""
import logging
from fastapi import APIRouter

logger = logging.getLogger("ai_workforce.routers.voice")

router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])


@router.get("/providers")
async def list_voice_providers():
    """List available TTS providers."""
    return {
        "providers": [
            {"id": "openai", "name": "OpenAI TTS", "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]},
            {"id": "deepgram", "name": "Deepgram", "voices": []},
        ]
    }
