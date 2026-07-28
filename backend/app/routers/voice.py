"""
Voice Router - API endpoints for text-to-speech and voice services
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.schemas import ChatResponse

logger = logging.getLogger("ai_workforce.routers.voice")

router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])


class TTSScriptRequest(BaseModel):
    """Request schema for text-to-speech."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice: Optional[str] = Field(default=None, description="Voice name")
    model: Optional[str] = Field(default=None, description="TTS model")
    provider: Optional[str] = Field(default=None, description="TTS provider override")


@router.post("/tts")
async def text_to_speech(request: TTSScriptRequest):
    """
    Convert text to speech audio.

    Args:
        request: TTS script request

    Returns:
        Audio file info
    """
    try:
        from app.services.voice_service import VoiceService
        voice_service = VoiceService()
        result = voice_service.generate_speech(
            text=request.text,
            voice=request.voice,
            model=request.model,
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "TTS failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/voices")
async def list_voices():
    """List available voice options."""
    try:
        from app.services.voice_service import VoiceService
        voice_service = VoiceService()
        return {"voices": voice_service.get_available_voices()}
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        return {"voices": []}
