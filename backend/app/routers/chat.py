"""
Chat Router - Async chat endpoints with streaming and history
"""
import logging
import time
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.schemas import ChatRequest, ChatResponse, ChatStreamChunk, ConversationMessage
from app.core.config import settings
from app.middleware.rate_limit import limiter
from app.services.llm.factory import LLMFactory
from app.services.monitoring import metrics
from app.database.session import get_db
from app.database.models import Conversation, ChatSession

logger = logging.getLogger("ai_workforce.routers.chat")

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT)
async def chat(request: Request, chat_req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Send a chat message to an LLM provider with automatic fallback.
    Persists conversation history to database.
    """
    session_id = chat_req.session_id or str(uuid.uuid4())
    start_time = time.time()

    try:
        # Get or create chat session
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            session = ChatSession(session_id=session_id, title=chat_req.message[:50])
            db.add(session)
            await db.flush()

        # Save user message
        db.add(Conversation(
            session_id=session_id,
            role="user",
            content=chat_req.message,
            provider=chat_req.provider.value,
            model=chat_req.model,
        ))

        # Call LLM with fallback
        result = await LLMFactory.generate(
            prompt=chat_req.message,
            provider=chat_req.provider.value,
            model=chat_req.model,
            temperature=chat_req.temperature,
            max_tokens=chat_req.max_tokens,
            system_prompt=chat_req.system_prompt,
        )

        duration = time.time() - start_time

        # Check for errors
        if result.get("error"):
            logger.error(f"LLM error: {result['error']} - {result.get('detail', '')}")
            raise HTTPException(status_code=503, detail=result.get("detail", "LLM service unavailable"))

        # Save assistant response
        usage = result.get("usage", {})
        db.add(Conversation(
            session_id=session_id,
            role="assistant",
            content=result["content"],
            provider=result.get("provider", chat_req.provider.value),
            model=result.get("model", chat_req.model or settings.OPENAI_MODEL),
            tokens_used=usage.get("total_tokens", 0),
        ))

        await db.commit()

        # Record metrics
        metrics.record_llm_request(
            provider=result.get("_provider_used", chat_req.provider.value),
            model=result.get("model", "unknown"),
            status="success",
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            cost_usd=result.get("cost_usd", 0.0),
            duration=result.get("_duration_seconds", duration),
        )

        return ChatResponse(
            provider=chat_req.provider,
            model=result.get("model", chat_req.model or settings.OPENAI_MODEL),
            response=result["content"],
            usage=usage,
            session_id=session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/stream")
@limiter.limit(settings.RATE_LIMIT)
async def chat_stream(request: Request, chat_req: ChatRequest):
    """Stream chat response from LLM."""
    session_id = chat_req.session_id or str(uuid.uuid4())

    async def event_generator():
        try:
            async for chunk in LLMFactory.generate_stream(
                prompt=chat_req.message,
                provider=chat_req.provider.value,
                model=chat_req.model,
                temperature=chat_req.temperature,
                max_tokens=chat_req.max_tokens,
                system_prompt=chat_req.system_prompt,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: [ERROR: {str(e)}]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Session-ID": session_id,
            "Cache-Control": "no-cache",
        },
    )


@router.get("/history/{session_id}", response_model=list[ConversationMessage])
async def get_chat_history(session_id: str, db: AsyncSession = Depends(get_db), limit: int = 50):
    """Get conversation history for a session."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        ConversationMessage(
            role=msg.role,
            content=msg.content,
            tokens_used=msg.tokens_used,
            created_at=msg.created_at,
        )
        for msg in reversed(messages)
    ]


@router.get("/providers")
async def list_providers():
    """List available LLM providers with models."""
    available = LLMFactory.list_available()
    all_providers = {
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "available": "openai" in available,
        },
        "gemini": {
            "name": "Google Gemini",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
            "available": "gemini" in available,
        },
        "deepseek": {
            "name": "DeepSeek",
            "models": ["deepseek-v4-flash", "deepseek-v4-pro"],
            "available": "deepseek" in available,
        },
    }
    return {
        "providers": all_providers,
        "fallback_order": settings.LLM_FALLBACK_ORDER,
    }
