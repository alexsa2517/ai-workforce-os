"""Routers module."""
from .chat import router as chat_router
from .agents import router as agents_router
from .health import router as health_router
from .auth import router as auth_router
from .video import router as video_router

__all__ = ["chat_router", "agents_router", "health_router", "auth_router", "video_router"]
