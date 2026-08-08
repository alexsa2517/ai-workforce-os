"""
AI Brain - Central intelligence with persistent context
Manages conversation history via database and coordinates AI services.
"""
import logging
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.services.llm.factory import LLMFactory
from app.core.config import settings
from app.database.models import Conversation, AIAgent

logger = logging.getLogger("ai_workforce.brain")


class Brain:
    """Central AI Brain with persistent conversation context."""

    def __init__(self, provider: str = "openai", session_id: Optional[str] = None):
        self.provider = provider
        self.session_id = session_id or str(uuid.uuid4())
        self.system_prompt = (
            "You are an AI Employee in the AI Workforce OS system. "
            "You are professional, helpful, and capable of handling various tasks. "
            "Always respond in the same language as the user. "
            "Be concise but thorough."
        )
        self.max_context_messages = 20
        logger.info(f"Brain initialized: provider={provider}, session={self.session_id}")

    async def process(
        self,
        message: str,
        db: AsyncSession,
        system_prompt: Optional[str] = None,
        context_limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Process message with persistent context from database.

        Args:
            message: User message
            db: Database session
            system_prompt: Override system prompt
            context_limit: Number of previous messages to include

        Returns:
            Dict with response, usage, and metadata
        """
        logger.info(f"Processing message (length={len(message)}, session={self.session_id})")

        # Fetch conversation history
        result = await db.execute(
            select(Conversation)
            .where(Conversation.session_id == self.session_id)
            .order_by(desc(Conversation.created_at))
            .limit(context_limit)
        )
        history = result.scalars().all()

        # Build messages
        messages = [{"role": "system", "content": system_prompt or self.system_prompt}]
        for msg in reversed(history):
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        # Save user message
        db.add(Conversation(
            session_id=self.session_id,
            role="user",
            content=message,
        ))

        # Generate response
        try:
            result = await LLMFactory.generate(
                prompt=message,
                provider=self.provider,
                system_prompt=system_prompt or self.system_prompt,
            )

            if result.get("error"):
                logger.error(f"Brain LLM error: {result['error']}")
                return {
                    "response": f"I apologize, but I encountered an error: {result.get('detail', 'Unknown error')}",
                    "error": result["error"],
                    "session_id": self.session_id,
                }

            response_text = result["content"]
            usage = result.get("usage", {})

            # Save assistant response
            db.add(Conversation(
                session_id=self.session_id,
                role="assistant",
                content=response_text,
                provider=result.get("provider"),
                model=result.get("model"),
                tokens_used=usage.get("total_tokens", 0),
            ))

            await db.commit()

            return {
                "response": response_text,
                "usage": usage,
                "provider": result.get("_provider_used", self.provider),
                "model": result.get("model"),
                "session_id": self.session_id,
                "cost_usd": result.get("cost_usd", 0.0),
            }

        except Exception as e:
            logger.error(f"Brain processing error: {e}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "error": "processing_error",
                "session_id": self.session_id,
            }

    async def get_context(self, db: AsyncSession, limit: int = 50) -> List[Dict[str, str]]:
        """Get conversation context for this session."""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.session_id == self.session_id)
            .order_by(desc(Conversation.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    async def clear_context(self, db: AsyncSession) -> None:
        """Clear conversation history for this session."""
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == self.session_id)
        )
        for msg in result.scalars().all():
            await db.delete(msg)
        await db.commit()
        logger.info(f"Context cleared for session {self.session_id}")
