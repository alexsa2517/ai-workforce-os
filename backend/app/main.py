"""
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
    from app.routers.pipeline import router as pipeline_router
    app.include_router(pipeline_router)
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
