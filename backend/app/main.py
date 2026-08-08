"""
AI Workforce OS - Main Application Entry Point
FastAPI application with async database, Redis cache, security middleware, and video generation.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.auth_middleware import APIKeyMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import setup_error_handlers
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.database.session import init_db, close_db
from app.services.cache_service import cache_service

import logging

setup_logging()
logger = logging.getLogger("ai_workforce.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Initialize cache
    try:
        await cache_service.initialize()
        logger.info("Cache service initialized")
    except Exception as e:
        logger.warning(f"Cache initialization failed: {e}")

    yield

    # Cleanup
    logger.info("Shutting down...")
    await close_db()
    await cache_service.close()
    logger.info("Cleanup complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Operating System for AI Employees with Video Generation",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)

# CORS - Restricted to configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    max_age=600,
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(APIKeyMiddleware)

# Error handlers
setup_error_handlers(app)

# Routers
from app.routers import chat_router, agents_router, health_router, auth_router, video_router

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(agents_router)
app.include_router(video_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "features": ["chat", "agents", "video_generation"],
        "docs": "/docs" if settings.APP_DEBUG else None,
    }
