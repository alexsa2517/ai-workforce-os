"""
Database Models - SQLAlchemy ORM models for AI Workforce OS
Defines all database tables and relationships.
"""
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, JSON, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

# Import Base from the unified session module to ensure consistent metadata
from database.session import Base


class JsonString(TypeDecorator):
    """JSON type that stores as TEXT for SQLite compatibility."""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class AIAgent(Base):
    """AI Agent record."""
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="idle")
    capabilities = Column(JsonString, nullable=True)
    config = Column(JsonString, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_active = Column(DateTime, nullable=True)

    # Relationships
    tasks = relationship("AITask", back_populates="agent", cascade="all, delete-orphan")


class AITask(Base):
    """AI Task record."""
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    agent_id = Column(String(255), ForeignKey("ai_agents.agent_id"), nullable=False)
    task_type = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    status = Column(String(50), default="pending")
    parameters = Column(JsonString, nullable=True)
    result = Column(JsonString, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("AIAgent", back_populates="tasks")


class ChatSession(Base):
    """Chat session record."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(255), nullable=False)
    system_prompt = Column(Text, nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2048)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message record."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
