"""
Application Configuration

Central configuration management using environment variables.
All settings can be overridden via .env file or environment variables.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file from project root
_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = Field(default="AI Workforce OS", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    APP_HOST: str = Field(default="0.0.0.0", description="Host to bind")
    APP_PORT: int = Field(default=8000, description="Port to bind")
    APP_DEBUG: bool = Field(default=False, description="Debug mode")

    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI model name")

    # Google Gemini
    GOOGLE_API_KEY: str = Field(default="", description="Google API key")
    GEMINI_MODEL: str = Field(default="gemini-pro", description="Gemini model name")

    # DeepSeek
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API key")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", description="DeepSeek model name")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./ai_workforce.db",
        description="Database connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")

    # Voice & Media
    TTS_PROVIDER: str = Field(default="openai", description="TTS provider")
    TTS_VOICE: str = Field(default="alloy", description="TTS voice")
    TTS_MODEL: str = Field(default="tts-1", description="TTS model")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    LOG_FILE: str = Field(default="logs/ai_workforce.log", description="Log file path")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")

    # Director AI
    DIRECTOR_AI_ENABLED: bool = Field(default=True, description="Enable Director AI agent")
    KNOWLEDGE_BASE_PATH: str = Field(
        default="./knowledge/director-ai",
        description="Knowledge base path"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings (dependency injection compatible)."""
    return settings
