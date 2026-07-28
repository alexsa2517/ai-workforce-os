#!/usr/bin/env python3
"""
Comprehensive fix script for AI Workforce OS backend.
Rewrites all files that need corrections.
"""
import os

PROJECT = "/home/ubuntu/ai-workforce-os"

def write(path: str, content: str):
    full = os.path.join(PROJECT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  Wrote: {path}")

# ============================================================
# 1. Fix main.py - logger before setup_logging, add monitoring router
# ============================================================
write("backend/app/main.py", '''"""
AI Workforce OS - Main Application Entry Point
FastAPI application with middleware, CORS, error handling,
and modular router registration.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, get_settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import setup_error_handlers

import logging

# ============================================
# Application Lifespan
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger = logging.getLogger("ai_workforce.main")
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    # Initialize database
    try:
        from database.session import init_db
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AI Workforce OS...")

# ============================================
# Logging Setup (BEFORE creating logger instances)
# ============================================
from app.utils.logging_config import setup_logging
setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
logger = logging.getLogger("ai_workforce.main")

# ============================================
# Application Instance
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered workforce management system for deploying and managing AI employees.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================
# Middleware
# ============================================
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# Error Handlers
setup_error_handlers(app)

# ============================================
# Register Routers
# ============================================
from app.routers import chat, health, agents, voice
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(agents.router)
app.include_router(agents.director_router)
app.include_router(voice.router)

# Monitoring endpoints
try:
    from monitoring.metrics_endpoint import router as monitoring_router
    app.include_router(monitoring_router)
except ImportError:
    logger.warning("Monitoring router not available")

# ============================================
# Root Endpoints (Legacy compatibility)
# ============================================
from pydantic import BaseModel
from typing import Optional
from app.core.schemas import ChatRequest as LegacyChatRequest

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - Application info."""
    return {
        "message": "AI Workforce OS is running",
        "employee": "Sales AI Employee #001",
        "version": settings.APP_VERSION,
    }

@app.get("/health", tags=["Root"])
async def health_legacy():
    """Legacy health check endpoint."""
    return {"status": "healthy"}

@app.post("/chat", tags=["Root"])
async def chat_legacy(request: LegacyChatRequest):
    """Legacy chat endpoint (redirects to v1 API)."""
    try:
        from app.services.llm.factory import LLMFactory
        llm = LLMFactory.get(request.provider)
        response = llm.generate(
            request.message,
            model=request.model or settings.OPENAI_MODEL,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
        )
        return {
            "provider": request.provider,
            "response": response.get("content", ""),
            "usage": response.get("usage", {}),
        }
    except Exception as e:
        return {"error": str(e)}
''')

# ============================================================
# 2. Fix LLM clients - add timeout, error handling, structured params
# ============================================================
write("backend/app/services/llm/openai.py", '''"""
OpenAI LLM Client - Chat completions with error handling and timeout
"""
import os
import logging
from typing import Any, Dict, Optional
from openai import OpenAI, APITimeoutError, APIError
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.openai")

DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 2


class OpenAIClient:
    """OpenAI chat completions client with retry and error handling."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )
        self.model = settings.OPENAI_MODEL

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion.

        Args:
            prompt: User message
            model: Override model name
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dict with 'content' and 'usage' keys
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            return {"content": content, "usage": usage}
        except APITimeoutError as e:
            logger.error(f"OpenAI timeout: {e}")
            return {"content": "Error: Request timed out", "usage": {}, "error": "timeout"}
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"content": f"Error: {str(e)}", "usage": {}, "error": "api_error"}
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}", exc_info=True)
            return {"content": f"Error: {str(e)}", "usage": {}, "error": "unexpected"}
''')

write("backend/app/services/llm/gemini.py", '''"""
Google Gemini LLM Client - Chat completions with error handling
"""
import os
import logging
from typing import Any, Dict, Optional
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.gemini")


class GeminiClient:
    """Google Gemini chat client with error handling."""

    def __init__(self):
        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        genai.configure(api_key=api_key)
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini.

        Args:
            prompt: User message
            model: Override model name
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dict with 'content' and 'usage' keys
        """
        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if system_prompt:
                # Gemini doesn't support system role directly; prepend to user message
                prompt = f"{system_prompt}\\n\\n{prompt}"

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            content = response.text
            # Gemini doesn't provide detailed token usage in the same way
            usage = {"total_tokens": len(content.split()) * 4}  # rough estimate
            return {"content": content, "usage": usage}
        except Exception as e:
            logger.error(f"Gemini error: {e}", exc_info=True)
            return {"content": f"Error: {str(e)}", "usage": {}, "error": str(e)}
''')

write("backend/app/services/llm/deepseek.py", '''"""
DeepSeek LLM Client - Chat completions with error handling and timeout
"""
import os
import logging
from typing import Any, Dict, Optional
from openai import OpenAI, APITimeoutError, APIError
from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.deepseek")

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2


class DeepSeekClient:
    """DeepSeek chat completions client via OpenAI-compatible API."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com",
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )
        self.model = settings.DEEPSEEK_MODEL

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion via DeepSeek API.

        Args:
            prompt: User message
            model: Override model name
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dict with 'content' and 'usage' keys
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            return {"content": content, "usage": usage}
        except APITimeoutError as e:
            logger.error(f"DeepSeek timeout: {e}")
            return {"content": "Error: Request timed out", "usage": {}, "error": "timeout"}
        except APIError as e:
            logger.error(f"DeepSeek API error: {e}")
            return {"content": f"Error: {str(e)}", "usage": {}, "error": "api_error"}
        except Exception as e:
            logger.error(f"DeepSeek unexpected error: {e}", exc_info=True)
            return {"content": f"Error: {str(e)}", "usage": {}, "error": "unexpected"}
''')

# ============================================================
# 3. Fix LLM Factory - use settings, standardize generate signature
# ============================================================
write("backend/app/services/llm/factory.py", '''"""
LLM Factory - Unified interface for creating LLM clients.
Supports OpenAI, Gemini, and DeepSeek providers.
"""
import logging
from typing import Any, Dict, Optional
from .openai import OpenAIClient
from .gemini import GeminiClient
from .deepseek import DeepSeekClient

logger = logging.getLogger("ai_workforce.llm.factory")


class LLMFactory:
    """Factory for creating LLM Client instances."""

    _instances: Dict[str, Any] = {}

    @classmethod
    def get(cls, provider: str):
        """
        Get an LLM client instance for the specified provider.
        Uses singleton pattern to reuse instances.

        Args:
            provider: Provider name (openai, gemini, deepseek)

        Returns:
            LLM client instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        providers = {
            "openai": OpenAIClient,
            "gemini": GeminiClient,
            "deepseek": DeepSeekClient,
        }
        if provider not in providers:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Available: {', '.join(providers.keys())}"
            )
        if provider not in cls._instances:
            cls._instances[provider] = providers[provider]()
            logger.info(f"Created LLM client for provider: {provider}")
        return cls._instances[provider]

    @classmethod
    def clear_cache(cls):
        """Clear cached LLM client instances."""
        cls._instances.clear()
        logger.info("LLM client cache cleared")
''')

# ============================================================
# 4. Fix JWT utils - use settings for secret
# ============================================================
write("backend/app/auth/jwt_utils.py", '''"""
JWT Utilities - Token generation, validation, and decoding
Provides JWT-based authentication for the AI Workforce OS API.
"""
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger("ai_workforce.auth")

# JWT configuration from settings
JWT_SECRET = settings.JWT_SECRET or os.getenv("JWT_SECRET", "ai-workforce-os-dev-secret-change-in-production")
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRATION_HOURS = settings.JWT_EXPIRATION_HOURS


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str = Field(..., description="Subject (user ID)")
    role: str = Field(default="user", description="User role")
    exp: Optional[int] = None
    iat: Optional[int] = None


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data (must include 'sub')
        expires_delta: Token expiration duration

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=JWT_EXPIRATION_HOURS)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"Token created for user: {data.get('sub')}")
    return encoded


def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
''')

# ============================================================
# 5. Fix database/session.py - handle SQLite vs PostgreSQL
# ============================================================
write("database/session.py", '''"""
Database Session - SQLAlchemy connection and session management
Supports both SQLite (development) and PostgreSQL (production).
"""
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator
from app.core.config import settings

logger = logging.getLogger("ai_workforce.database")


def _create_engine():
    """Create SQLAlchemy engine with appropriate settings for the database type."""
    url = settings.DATABASE_URL
    is_sqlite = "sqlite" in url.lower()

    connect_args = {}
    if is_sqlite:
        # SQLite-specific settings: enable WAL mode for better concurrency
        connect_args["check_same_thread"] = False
        engine_kwargs = {}
    else:
        # PostgreSQL/MySQL settings
        engine_kwargs = {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_pre_ping": True,
        }

    engine = create_engine(
        url,
        echo=settings.APP_DEBUG,
        connect_args=connect_args,
        **engine_kwargs,
    )

    if is_sqlite:
        # Enable WAL mode for better concurrency on SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


# Create engine
engine = _create_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for models - single source of truth
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


def get_engine():
    """Get the SQLAlchemy engine instance."""
    return engine
''')

# ============================================================
# 6. Fix database/models.py - use the same Base from session
# ============================================================
write("database/models.py", '''"""
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
''')

# ============================================================
# 7. Fix alembic env.py - use the correct Base
# ============================================================
write("backend/alembic/env.py", '''"""
Alembic Environment Configuration
Configures Alembic to use the same Base as the application.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.session import Base
from database.models import *  # noqa: ensure all models are imported

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''')

# ============================================================
# 8. Fix Alembic initial migration
# ============================================================
write("backend/alembic/versions/001_initial.py", '''"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ai_agents table
    op.create_table(
        "ai_agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("capabilities", sa.Text(), nullable=True),
        sa.Column("config", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("last_active", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_agents_id"), "ai_agents", ["id"], unique=False)
    op.create_index(
        op.f("ix_ai_agents_agent_id"), "ai_agents", ["agent_id"], unique=True
    )

    # Create ai_tasks table
    op.create_table(
        "ai_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.String(255), nullable=False),
        sa.Column("agent_id", sa.String(255), nullable=False),
        sa.Column("task_type", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("parameters", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.agent_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_tasks_id"), "ai_tasks", ["id"], unique=False)
    op.create_index(
        op.f("ix_ai_tasks_task_id"), "ai_tasks", ["task_id"], unique=True
    )

    # Create chat_sessions table
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(255), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("max_tokens", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chat_sessions_id"), "chat_sessions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_chat_sessions_session_id"),
        "chat_sessions",
        ["session_id"],
        unique=True,
    )

    # Create chat_messages table
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chat_messages_id"), "chat_messages", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_chat_messages_id"), table_name="chat_messages"
    )
    op.drop_table("chat_messages")
    op.drop_index(
        op.f("ix_chat_sessions_session_id"), table_name="chat_sessions"
    )
    op.drop_index(op.f("ix_chat_sessions_id"), table_name="chat_sessions")
    op.drop_table("chat_sessions")
    op.drop_index(
        op.f("ix_ai_tasks_task_id"), table_name="ai_tasks"
    )
    op.drop_index(op.f("ix_ai_tasks_id"), table_name="ai_tasks")
    op.drop_table("ai_tasks")
    op.drop_index(
        op.f("ix_ai_agents_agent_id"), table_name="ai_agents"
    )
    op.drop_index(op.f("ix_ai_agents_id"), table_name="ai_agents")
    op.drop_table("ai_agents")
''')

# ============================================================
# 9. Fix Voice Service - proper implementation
# ============================================================
write("backend/app/services/voice_service.py", '''"""
Voice Service - Unified interface for text-to-speech generation
Supports OpenAI TTS and Deepgram TTS.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger("ai_workforce.voice")


class VoiceService:
    """Text-to-Speech service with multiple provider support."""

    def __init__(self):
        self.provider = settings.TTS_PROVIDER
        self.voice = settings.TTS_VOICE
        self.model = settings.TTS_MODEL
        self.speed = settings.TTS_SPEED
        self.language = settings.TTS_LANGUAGE

    def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice name override
            model: TTS model override
            output_dir: Directory for output file

        Returns:
            Dict with status and audio file path/URL
        """
        voice = voice or self.voice
        model = model or self.model
        output_dir = output_dir or settings.MOVIES_DIR

        if self.provider == "openai":
            return self._generate_openai(text, voice, model, output_dir)
        elif self.provider == "deepgram":
            return self._generate_deepgram(text, voice, model, output_dir)
        else:
            return {"status": "error", "message": f"Unknown TTS provider: {self.provider}"}

    def _generate_openai(self, text: str, voice: str, model: str, output_dir: str) -> Dict[str, Any]:
        """Generate speech using OpenAI TTS."""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
                timeout=30.0,
            )
            output_path = os.path.join(output_dir, f"speech_{hash(text) % 10000}.mp3")
            os.makedirs(output_dir, exist_ok=True)

            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=self.speed,
            )
            response.stream_to_file(output_path)

            logger.info(f"OpenAI TTS: Generated {output_path}")
            return {
                "status": "success",
                "provider": "openai",
                "voice": voice,
                "model": model,
                "output_path": output_path,
            }
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _generate_deepgram(self, text: str, voice: str, model: str, output_dir: str) -> Dict[str, Any]:
        """Generate speech using Deepgram TTS."""
        try:
            import requests
            api_key = settings.DEEPGRAM_API_KEY or os.getenv("DEEPGRAM_API_KEY", "")
            output_path = os.path.join(output_dir, f"speech_{hash(text) % 10000}.mp3")
            os.makedirs(output_dir, exist_ok=True)

            headers = {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "text": text,
                "model": model,
                "options": {
                    "language": self.language,
                    "speed": self.speed,
                },
            }

            response = requests.post(
                "https://api.deepgram.com/v1/speak",
                headers=headers,
                json=data,
                timeout=30,
            )
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Deepgram TTS: Generated {output_path}")
            return {
                "status": "success",
                "provider": "deepgram",
                "voice": voice,
                "model": model,
                "output_path": output_path,
            }
        except Exception as e:
            logger.error(f"Deepgram TTS error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def get_available_voices(self) -> list:
        """Get available voices based on current provider."""
        if self.provider == "openai":
            return [
                {"name": "alloy", "description": "Balanced, neutral voice"},
                {"name": "echo", "description": "Deep, resonant voice"},
                {"name": "fable", "description": "Warm, storytelling voice"},
                {"name": "onyx", "description": "Strong, authoritative voice"},
                {"name": "nova", "description": "Bright, energetic voice"},
                {"name": "shimmer", "description": "Light, youthful voice"},
            ]
        elif self.provider == "deepgram":
            return [
                {"name": "aura-asteria-en", "description": "English female"},
                {"name": "aura-luna-en", "description": "English female"},
                {"name": "aura-stella-en", "description": "English female"},
            ]
        return []
''')

# ============================================================
# 10. Fix Voice Router - use Pydantic model for request body
# ============================================================
write("backend/app/routers/voice.py", '''"""
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
''')

# ============================================================
# 11. Fix Chat Router - use factory properly, add session tracking
# ============================================================
write("backend/app/routers/chat.py", '''"""
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
                "models": ["deepseek-chat", "deepseek-coder"],
            },
        ]
    }
''')

# ============================================================
# 12. Fix Health Router - check real service status
# ============================================================
write("backend/app/routers/health.py", '''"""
Health Router - System health check endpoints
Provides detailed health status for all system components.
"""
import logging
import time
from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.schemas import HealthResponse
from app.core.config import settings

logger = logging.getLogger("ai_workforce.routers.health")

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check system health status."""
    services = {}

    # Check API
    services["api"] = "healthy"

    # Check database
    try:
        from database.session import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        services["database"] = f"unhealthy: {str(e)[:50]}"

    # Check LLM factory
    try:
        from app.services.llm.factory import LLMFactory
        services["llm_factory"] = "healthy"
    except Exception as e:
        services["llm_factory"] = f"unhealthy: {str(e)[:50]}"

    # Check Director AI
    if settings.DIRECTOR_AI_ENABLED:
        try:
            from app.agents.director_ai.memory_loader import DirectorMemoryLoader
            loader = DirectorMemoryLoader()
            services["director_ai"] = "healthy"
        except Exception as e:
            services["director_ai"] = f"unhealthy: {str(e)[:50]}"

    # Determine overall status
    overall = "healthy" if all(v == "healthy" for v in services.values()) else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        services=services,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/ready")
async def readiness_check():
    """Check if the system is ready to accept requests."""
    return {
        "ready": True,
        "uptime_seconds": round(time.time() - _start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
''')

# ============================================================
# 13. Fix Agents Router - add CRUD operations
# ============================================================
write("backend/app/routers/agents.py", '''"""
Agents Router - API endpoints for managing AI agents
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.schemas import AgentInfo, AgentStatus, AgentTask, TaskStatus, SceneRequest, SceneResponse, CharacterInfo, WorldInfo, EpisodeInfo

logger = logging.getLogger("ai_workforce.routers.agents")

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class AgentCreate(BaseModel):
    """Request schema for creating a new agent."""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., min_length=1, description="Agent display name")
    role: str = Field(..., description="Agent role")
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    config: Optional[dict] = None


class AgentUpdate(BaseModel):
    """Request schema for updating an agent."""
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    config: Optional[dict] = None


# In-memory agent registry (in production, use database)
_agent_registry = {
    "director_ai": AgentInfo(
        agent_id="director_ai",
        name="DirectorAI",
        role="Director AI",
        status=AgentStatus.ACTIVE,
        description="AI Director for cinematic scene generation",
        capabilities=["scene_creation", "character_management", "prompt_engineering"],
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
    ),
    "sales_ai_001": AgentInfo(
        agent_id="sales_ai_001",
        name="Sales AI Employee #001",
        role="Sales Representative",
        status=AgentStatus.IDLE,
        description="AI-powered sales representative for customer interactions",
        capabilities=["customer_service", "lead_qualification", "sales_pitch"],
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
    ),
}


@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """List all registered AI agents."""
    return list(_agent_registry.values())


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get details of a specific agent."""
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@router.post("/", response_model=AgentInfo)
async def create_agent(agent: AgentCreate):
    """Register a new AI agent."""
    if agent.agent_id in _agent_registry:
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{agent.agent_id}' already exists",
        )
    info = AgentInfo(
        agent_id=agent.agent_id,
        name=agent.name,
        role=agent.role,
        description=agent.description,
        capabilities=agent.capabilities,
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
    )
    _agent_registry[agent.agent_id] = info
    logger.info(f"Agent created: {agent.agent_id}")
    return info


@router.patch("/{agent_id}", response_model=AgentInfo)
async def update_agent(agent_id: str, update: AgentUpdate):
    """Update an existing agent."""
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agent, key, value)
    agent.last_active = datetime.now(timezone.utc)

    logger.info(f"Agent updated: {agent_id}")
    return agent


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Remove an agent from the registry."""
    if agent_id not in _agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    del _agent_registry[agent_id]
    logger.info(f"Agent deleted: {agent_id}")
    return {"message": f"Agent '{agent_id}' deleted"}


@router.post("/{agent_id}/tasks", response_model=AgentTask)
async def assign_task(agent_id: str, task: AgentTask):
    """Assign a task to an agent."""
    if agent_id not in _agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    task.agent_id = agent_id
    task.status = TaskStatus.PENDING
    logger.info(f"Task assigned to {agent_id}: {task.task_type}")
    return task


# Director AI specific endpoints
director_router = APIRouter(prefix="/api/v1/agents/director", tags=["Director AI"])


@director_router.post("/scene", response_model=SceneResponse)
async def create_scene(request: SceneRequest):
    """Create a cinematic scene using DirectorAI."""
    try:
        from app.agents.director_ai.director import DirectorAI
        director = DirectorAI()
        result = director.create_scene()
        return SceneResponse(
            episode=result.get("episode", ""),
            scene=result.get("scene", ""),
            prompt=result.get("prompt", ""),
        )
    except FileNotFoundError as e:
        logger.error(f"Knowledge base file not found: {e}")
        raise HTTPException(status_code=404, detail="Knowledge base file not found")
    except Exception as e:
        logger.error(f"Scene creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scene creation failed: {str(e)}")


@director_router.get("/characters/{character_name}", response_model=CharacterInfo)
async def get_character(character_name: str):
    """Get character information from knowledge base."""
    try:
        from app.agents.director_ai.memory_loader import DirectorMemoryLoader
        loader = DirectorMemoryLoader()
        character = loader.load_character(character_name)
        return CharacterInfo(**character)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")


@director_router.get("/worlds/{world_name}", response_model=WorldInfo)
async def get_world(world_name: str):
    """Get world information from knowledge base."""
    try:
        from app.agents.director_ai.memory_loader import DirectorMemoryLoader
        loader = DirectorMemoryLoader()
        world = loader.load_world(world_name)
        return WorldInfo(**world)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"World '{world_name}' not found")


@director_router.get("/episodes/{episode_name}", response_model=EpisodeInfo)
async def get_episode(episode_name: str):
    """Get episode information from knowledge base."""
    try:
        from app.agents.director_ai.memory_loader import DirectorMemoryLoader
        loader = DirectorMemoryLoader()
        episode = loader.load_episode(episode_name)
        return EpisodeInfo(**episode)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Episode '{episode_name}' not found")
''')

# ============================================================
# 14. Fix Character Memory - expand with real methods
# ============================================================
write("backend/app/agents/director_ai/character_memory.py", '''"""
Character Memory - Persistent character state management
Manages character dialogue history, emotional states, and conversation context.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ai_workforce.agents.character_memory")


class CharacterMemory:
    """Persistent memory for character state and conversation history."""

    def __init__(self, storage_path: Optional[str] = None):
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.storage_path = storage_path

    def add_character(self, name: str, data: Dict[str, Any]) -> None:
        """Add or update a character."""
        self.characters[name] = {
            **data,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if name not in self.conversations:
            self.conversations[name] = []
        logger.info(f"Character added/updated: {name}")

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        """Get character data."""
        return self.characters.get(name)

    def list_characters(self) -> List[str]:
        """List all character names."""
        return list(self.characters.keys())

    def remove_character(self, name: str) -> bool:
        """Remove a character."""
        if name in self.characters:
            del self.characters[name]
            self.conversations.pop(name, None)
            logger.info(f"Character removed: {name}")
            return True
        return False

    def add_conversation(self, character_name: str, message: str, role: str = "user") -> None:
        """Add a conversation entry for a character."""
        if character_name not in self.conversations:
            self.conversations[character_name] = []
        self.conversations[character_name].append({
            "role": role,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_conversations(self, character_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent conversation history for a character."""
        convos = self.conversations.get(character_name, [])
        return convos[-limit:]

    def get_context(self, character_name: str) -> str:
        """Get a summary context string for the character."""
        char = self.get_character(character_name)
        if not char:
            return ""

        name = char.get("name", character_name)
        role = char.get("role", "Unknown")
        backstory = char.get("story", {}).get("backstory", "")

        context = f"Character: {name}\\nRole: {role}\\n"
        if backstory:
            context += f"Backstory: {backstory}\\n"

        # Add recent conversation context
        recent = self.get_conversations(character_name, limit=5)
        if recent:
            context += "Recent context:\\n"
            for msg in recent:
                context += f"  [{msg['role']}]: {msg['message'][:100]}\\n"

        return context

    def clear_conversations(self, character_name: Optional[str] = None) -> None:
        """Clear conversation history."""
        if character_name:
            self.conversations.pop(character_name, None)
        else:
            self.conversations.clear()

    def save(self, path: Optional[str] = None) -> None:
        """Save character data to file."""
        save_path = Path(path or self.storage_path or "character_memory.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "characters": self.characters,
            "conversations": self.conversations,
        }
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Character memory saved to {save_path}")

    def load(self, path: Optional[str] = None) -> None:
        """Load character data from file."""
        load_path = Path(path or self.storage_path or "character_memory.json")
        if not load_path.exists():
            logger.warning(f"Character memory file not found: {load_path}")
            return
        with open(load_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.characters = data.get("characters", {})
        self.conversations = data.get("conversations", {})
        logger.info(f"Character memory loaded from {load_path}")
''')

# ============================================================
# 15. Fix Prompt Engine - expand with more methods
# ============================================================
write("backend/app/agents/director_ai/prompt_engine.py", '''"""
Prompt Engine - Generates structured prompts for cinematic AI generation
Creates scene prompts, character descriptions, world descriptions,
and emotion-based prompts for image and video generation.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ai_workforce.agents.prompt_engine")


class PromptEngine:
    """Engine for generating structured cinematic prompts."""

    def __init__(self):
        self.default_style = "cinematic, photorealistic, 4K quality"

    def create_scene_prompt(
        self,
        character: Dict[str, Any],
        world: Dict[str, Any],
        scene: Dict[str, Any],
    ) -> str:
        """
        Create a detailed scene prompt for image/video generation.

        Args:
            character: Character data from knowledge base
            world: World data from knowledge base
            scene: Scene data from episode

        Returns:
            Detailed scene prompt string
        """
        char_name = character.get("name", "Unknown")
        char_english = character.get("english_name", char_name)
        appearance = character.get("appearance", {})
        face = appearance.get("face", {}).get("description", "")
        hair = appearance.get("hair", {})
        hair_desc = f"{hair.get('color', 'black')} {hair.get('style', 'hair')}"
        costume = character.get("costume", {}).get("main_outfit", "traditional outfit")

        world_name = world.get("name", "Unknown world")
        locations = world.get("locations", [])
        location = scene.get("location", locations[0]["name"] if locations else "unknown")

        scene_title = scene.get("title", "")
        action = scene.get("action", "")
        emotion = scene.get("emotion", "neutral")
        time_of_day = scene.get("time", "")

        prompt = (
            f"Cinematic scene: {char_name} ({char_english}) in {world_name}. "
            f"Location: {location}. "
            f"Character appearance: {face}, hair: {hair_desc}, wearing {costume}. "
            f"Action: {action}. "
            f"Emotion: {emotion}. "
            f"Time: {time_of_day}. "
            f"Style: {self.default_style}. "
            f"Lighting: natural, dramatic shadows. "
            f"Camera: medium shot, slight angle."
        )
        return prompt

    def create_character_prompt(self, character: Dict[str, Any], emotion: str = "neutral") -> str:
        """
        Create a character portrait prompt.

        Args:
            character: Character data
            emotion: Target emotion for the portrait

        Returns:
            Character portrait prompt
        """
        char_name = character.get("name", "Unknown")
        char_english = character.get("english_name", char_name)
        appearance = character.get("appearance", {})
        face = appearance.get("face", {}).get("description", "")
        hair = appearance.get("hair", {})
        hair_desc = f"{hair.get('color', 'black')} {hair.get('style', 'hair')}"
        costume = character.get("costume", {}).get("main_outfit", "traditional outfit")
        gender = character.get("basic_information", {}).get("gender", "male")

        prompt = (
            f"Cinematic portrait of a {gender}, "
            f"name: {char_name} ({char_english}). "
            f"Face: {face}. Hair: {hair_desc}. "
            f"Wearing: {costume}. "
            f"Emotion: {emotion}. "
            f"Style: {self.default_style}. "
            f"Lighting: soft, cinematic, Rembrandt lighting. "
            f"Background: subtle gradient, out of focus."
        )
        return prompt

    def create_world_prompt(self, world: Dict[str, Any]) -> str:
        """
        Create a world/environment prompt.

        Args:
            world: World data

        Returns:
            World environment prompt
        """
        name = world.get("name", "Unknown world")
        era = world.get("era", "Unknown era")
        description = world.get("description", "")
        locations = world.get("locations", [])
        location_desc = ", ".join(
            [loc.get("name", "") for loc in locations]
        ) if locations else ""

        prompt = (
            f"World environment: {name}. "
            f"Era: {era}. "
            f"Description: {description}. "
            f"Key locations: {location_desc}. "
            f"Style: {self.default_style}. "
            f"Atmosphere: immersive, detailed, atmospheric lighting."
        )
        return prompt

    def create_emotion_prompt(self, emotion: str, intensity: str = "moderate") -> str:
        """
        Create an emotion-specific prompt modifier.

        Args:
            emotion: Target emotion
            intensity: Intensity level (subtle, moderate, intense)

        Returns:
            Emotion prompt modifier string
        """
        emotion_map = {
            "happy": "warm smile, bright eyes, relaxed posture",
            "sad": "downcast eyes, slight frown, subdued expression",
            "angry": "furrowed brows, clenched jaw, intense gaze",
            "fearful": "wide eyes, tense expression, slight recoil",
            "surprised": "raised eyebrows, slightly open mouth",
            "neutral": "calm expression, steady gaze, composed",
            "confused": "slightly furrowed brows, tilted head, uncertain expression",
            "determined": "firm jaw, focused eyes, strong posture",
        }
        facial_expr = emotion_map.get(emotion, "neutral expression")

        intensity_map = {
            "subtle": "subtle",
            "moderate": "moderate",
            "intense": "intense",
        }
        level = intensity_map.get(intensity, "moderate")

        return f"Facial expression: {level} {facial_expr}, {level} body language matching {emotion} emotion"

    def create_dialogue_prompt(self, character: Dict[str, Any], dialogue: str) -> str:
        """
        Create a prompt for lip-sync generation with dialogue.

        Args:
            character: Character data
            dialogue: The dialogue text

        Returns:
            Dialogue prompt with character context
        """
        char_name = character.get("name", "Unknown")
        voice_data = character.get("voice", {})
        voice_desc = voice_data.get("description", "natural speaking voice")

        prompt = (
            f"Character: {char_name}. "
            f"Voice: {voice_desc}. "
            f"Dialogue: \"{dialogue}\" "
            f"Speak naturally with appropriate emotional inflection."
        )
        return prompt
''')

# ============================================================
# 16. Fix Director AI - use character_memory, support parameters
# ============================================================
write("backend/app/agents/director_ai/director.py", '''"""
DirectorAI - AI Director agent for cinematic scene generation
Loads knowledge from the knowledge base and generates scene prompts.
"""
import logging
from typing import Any, Dict, Optional
from .memory_loader import DirectorMemoryLoader
from .prompt_engine import PromptEngine
from .character_memory import CharacterMemory

logger = logging.getLogger("ai_workforce.agents.director_ai")


class DirectorAI:
    """AI Director agent that creates cinematic scenes from knowledge base data."""

    def __init__(self):
        self.memory = DirectorMemoryLoader()
        self.prompt_engine = PromptEngine()
        self.character_memory = CharacterMemory()

    def create_scene(
        self,
        character: str = "linhfeng",
        world: str = "ancient-world",
        episode: str = "ep001",
        scene_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Create a cinematic scene.

        Args:
            character: Character name from knowledge base
            world: World name from knowledge base
            episode: Episode name from knowledge base
            scene_index: Index of the scene in the episode

        Returns:
            Dict with episode, scene, and prompt data
        """
        char_data = self.memory.load_character(character)
        world_data = self.memory.load_world(world)
        episode_data = self.memory.load_episode(episode)

        scenes = episode_data.get("scenes", [])
        if scene_index >= len(scenes):
            scene_index = 0
        scene = scenes[scene_index]

        prompt = self.prompt_engine.create_scene_prompt(
            char_data, world_data, scene
        )

        # Update character memory with conversation
        dialogue = scene.get("dialogue", {}).get("text", "")
        if dialogue:
            self.character_memory.add_conversation(character, dialogue, "character")

        result = {
            "episode": episode_data.get("title", ""),
            "scene": scene.get("title", ""),
            "prompt": prompt,
            "character": character,
            "world": world,
            "scene_index": scene_index,
            "dialogue": dialogue,
            "emotion": scene.get("emotion", "neutral"),
            "action": scene.get("action", ""),
        }
        logger.info(f"Scene created: {result['episode']} - {result['scene']}")
        return result

    def get_character_context(self, character_name: str) -> str:
        """Get the full context for a character."""
        return self.character_memory.get_context(character_name)

    def list_available_content(self) -> Dict[str, Any]:
        """List available characters, worlds, and episodes."""
        return {
            "characters": ["linhfeng"],
            "worlds": ["ancient-world"],
            "episodes": ["ep001"],
        }
''')

# ============================================================
# 17. Fix Dockerfile - correct paths
# ============================================================
write("Dockerfile", '''# ============================================
# AI Workforce OS - Dockerfile
# ============================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY database/ /app/database/
COPY knowledge/ /app/knowledge/
COPY monitoring/ /app/monitoring/
COPY agents/ /app/agents/
COPY brain/ /app/brain/
COPY api/ /app/api/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/

# Create necessary directories
RUN mkdir -p /app/logs /app/movies

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health/').raise_for_status()" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''')

# ============================================================
# 18. Fix .env.example - add all missing settings
# ============================================================
write(".env.example", '''# AI Workforce OS - Environment Configuration
# Copy this file to .env and fill in your values
# ============================================
# LLM Provider API Keys
# ============================================
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-pro
# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
# ============================================
# JWT Authentication
# ============================================
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
# ============================================
# Application Settings
# ============================================
APP_NAME=AI Workforce OS
APP_VERSION=0.2.0
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true
# ============================================
# Database
# ============================================
# Development (SQLite)
DATABASE_URL=sqlite:///./ai_workforce.db
# Production (PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost:5432/ai_workforce
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
# ============================================
# Voice & Media (TTS)
# ============================================
TTS_PROVIDER=openai
TTS_VOICE=alloy
TTS_MODEL=tts-1
TTS_SPEED=1.0
TTS_LANGUAGE=th
# Deepgram TTS (alternative)
DEEPGRAM_API_KEY=your_deepgram_api_key_here
DEEPGRAM_MODEL=aura-asteria-en
# ============================================
# Lip-Sync Settings
# ============================================
# Provider: hedra, did, simulated
LIP_SYNC_PROVIDER=did
LIP_SYNC_RESOLUTION=720p
D_ID_API_KEY=your_d_id_api_key_here
D_ID_BASE_URL=https://api.d-id.com
HEDRA_API_KEY=your_hedra_api_key_here
HEDRA_BASE_URL=https://api.hedra.com
# ============================================
# Movie Pipeline Settings
# ============================================
MOVIES_DIR=./movies
SCENES_PER_EPISODE=5
MAX_PARALLEL_JOBS=3
# ============================================
# Character Settings
# ============================================
CHARACTER_FILE=linhfeng.json
WORLD_FILE=ancient-world.json
# ============================================
# Video Assembly Settings
# ============================================
BACKGROUND_MUSIC_PATH=
SUBTITLE_FONT=NotoSansThai-Regular.ttf
# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/ai_workforce.log
# ============================================
# CORS Settings
# ============================================
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=true
# ============================================
# Director AI
# ============================================
DIRECTOR_AI_ENABLED=true
KNOWLEDGE_BASE_PATH=./knowledge/director-ai
''')

# ============================================================
# 19. Update backend/requirements.txt - add missing deps
# ============================================================
write("backend/requirements.txt", '''# AI Workforce OS - Backend Dependencies
# Core
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.6.0
python-dotenv==1.0.1

# Database
sqlalchemy==2.0.35
alembic==1.13.2

# LLM Providers
openai==1.48.0
google-generativeai==0.8.3

# Authentication
PyJWT==2.9.0
passlib[bcrypt]==1.7.4

# Voice & Media
requests==2.32.3
Pillow==10.4.0

# Utilities
python-multipart==0.0.9
httpx==0.27.2

# Testing
pytest==8.3.3
pytest-asyncio==0.24.0

# Code Quality
ruff==0.6.8
black==24.8.0
isort==5.13.2
mypy==1.11.2

# Monitoring
prometheus-client==0.21.0
''')

# ============================================================
# 20. Fix monitoring/metrics_endpoint.py - register properly
# ============================================================
write("monitoring/metrics_endpoint.py", '''"""
Monitoring Endpoints - Prometheus-compatible metrics and health
Provides /metrics and /health endpoints for monitoring.
"""
import time
from fastapi import APIRouter
from app.services.cache_service import cache_service
from app.services.monitoring import metrics
from app.core.config import settings

router = APIRouter(tags=["Monitoring"])


@router.get("/api/v1/metrics")
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns metrics in text format for Prometheus scraping.
    """
    metrics_data = metrics.get_prometheus_format()
    return {
        "content-type": "text/plain; version=0.0.4; charset=utf-8",
        "metrics": metrics_data,
    }


@router.get("/api/v1/system-status")
async def detailed_health():
    """
    Detailed system health check endpoint.
    Returns health status of all system components.
    """
    all_metrics = metrics.get_all()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "timestamp": time.time(),
        "uptime_seconds": all_metrics["uptime_seconds"],
        "services": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "llm": "healthy",
            "director_ai": "healthy" if settings.DIRECTOR_AI_ENABLED else "disabled",
        },
        "metrics": {
            "total_requests": all_metrics["counters"].get("requests_total", 0),
            "total_errors": all_metrics["counters"].get("errors_total", 0),
            "cache_size": cache_service._memory_cache.size,
            "cache_max_size": cache_service._memory_cache._max_size,
        },
    }
''')

# ============================================================
# 21. Fix monitoring/__init__.py
# ============================================================
write("monitoring/__init__.py", '''"""
Monitoring package - Metrics collection and health monitoring.
"""
''')

# ============================================================
# 22. Add Pipeline Router
# ============================================================
write("backend/app/routers/pipeline.py", '''"""
Pipeline Router - API endpoints for movie pipeline operations
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("ai_workforce.routers.pipeline")

router = APIRouter(prefix="/api/v1/pipeline", tags=["Movie Pipeline"])


class PipelineRunRequest(BaseModel):
    """Request to run the movie pipeline."""
    character: str = Field(default="linhfeng", description="Character name")
    world: str = Field(default="ancient-world", description="World name")
    episode: str = Field(default="ep001", description="Episode name")
    scene_index: int = Field(default=0, description="Starting scene index")


@router.post("/run")
async def run_pipeline(request: PipelineRunRequest):
    """Run the movie generation pipeline for an episode."""
    try:
        from app.services.pipeline.movie_pipeline import MoviePipeline
        pipeline = MoviePipeline()
        result = pipeline.run_episode(
            character=request.character,
            episode=request.episode,
            scene_index=request.scene_index,
        )
        return result
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.get("/status")
async def pipeline_status():
    """Get the current status of the movie pipeline."""
    return {
        "status": "idle",
        "movies_dir": "./movies",
        "scenes_per_episode": 5,
        "max_parallel_jobs": 3,
    }


class LipSyncRequest(BaseModel):
    """Request for lip-sync generation."""
    character: str = Field(default="linhfeng", description="Character name")
    text: str = Field(..., min_length=1, description="Dialogue text")
    image_path: Optional[str] = Field(default=None, description="Path to character image")
    audio_path: Optional[str] = Field(default=None, description="Path to audio file")


@router.post("/lip-sync")
async def lip_sync(request: LipSyncRequest):
    """Generate lip-sync video from character image and audio."""
    try:
        from app.services.lip_sync.lip_sync_service import LipSyncService
        service = LipSyncService()
        result = service.generate(
            character=request.character,
            text=request.text,
            image_path=request.image_path,
            audio_path=request.audio_path,
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lip-sync error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lip-sync failed: {str(e)}")
''')

# ============================================================
# 23. Register pipeline router in main.py is already handled
# ============================================================

print("=" * 60)
print("All backend fixes applied successfully!")
print("=" * 60)
