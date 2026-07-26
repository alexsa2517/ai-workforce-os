"""
Chat Router - API endpoints for chat interactions
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.services.llm.factory import LLMFactory
from app.core.schemas import ChatRequest, ChatResponse, LLMProvider

logger = logging.getLogger("ai_workforce.routers.chat")

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message to an AI provider and get a response.

    Args:
        request: Chat request with message and provider selection

    Returns:
        AI response with provider info and usage stats
    """
    try:
        logger.info(f"Chat request: provider={request.provider}, message_length={len(request.message)}")

        llm = LLMFactory.get(request.provider)

        # Use custom model if specified
        if request.model:
            llm.model = request.model

        # Build kwargs for generation
        gen_kwargs = {}
        if request.temperature is not None:
            gen_kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            gen_kwargs["max_tokens"] = request.max_tokens
        if request.system_prompt is not None:
            gen_kwargs["system_prompt"] = request.system_prompt

        response = llm.generate(request.message, **gen_kwargs)

        logger.info(f"Chat response received from {request.provider}")

        return ChatResponse(
            provider=request.provider,
            model=getattr(llm, "model", "unknown"),
            response=response if isinstance(response, str) else str(response),
        )

    except ValueError as e:
        logger.error(f"Invalid provider: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
