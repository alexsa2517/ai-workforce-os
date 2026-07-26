"""
Tests for application configuration
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.config import Settings, settings


def test_settings_defaults():
    """Test that settings have correct default values."""
    assert settings.APP_NAME == "AI Workforce OS"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.APP_PORT == 8000


def test_settings_llm_providers():
    """Test LLM provider settings exist."""
    assert hasattr(settings, "OPENAI_MODEL")
    assert hasattr(settings, "GEMINI_MODEL")
    assert hasattr(settings, "DEEPSEEK_MODEL")


def test_settings_database():
    """Test database settings exist."""
    assert hasattr(settings, "DATABASE_URL")
    assert "sqlite" in settings.DATABASE_URL or "postgresql" in settings.DATABASE_URL.lower()
