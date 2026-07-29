"""
Chat Router - API endpoints for chat interactions with LLM providers
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.core.schemas import ChatRequest, ChatResponse
from app.core.config import settings
from app.services.llm.factory import LLMFactory

logger = logging.getLogger("ai_workforce.routers.chat")

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message to an LLM provider.

    Args:
        request: Chat request with message, provider, and optional parameters

    Returns:
        ChatResponse with the generated response
    """
    try:
        llm = LLMFactory.get(request.provider)
        result = llm.generate(
            prompt=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
        )
        return ChatResponse(
            provider=request.provider,
            model=request.model or settings.OPENAI_MODEL,
            response=result.get("content", ""),
            usage=result.get("usage", {}),
        )
    except ValueError as e:
        logger.warning(f"Invalid provider: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/providers")
async def list_providers():
    """List available LLM providers."""
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
            },
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "models": ["deepseek-v4-flash", "deepseek-v4-pro"],
            },
        ]
    }
