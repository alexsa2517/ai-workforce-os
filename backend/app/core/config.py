"""
Application Configuration - Central configuration management.
All settings loaded from environment variables with strict validation.
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parents[3] / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)


class Settings(BaseSettings):
    """Application settings with strict validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = Field(default="AI Workforce OS", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_HOST: str = Field(default="0.0.0.0", description="Host to bind")
    APP_PORT: int = Field(default=8000, description="Port to bind")
    APP_DEBUG: bool = Field(default=False, description="Debug mode")

    # Security
    API_KEY: str = Field(default="", description="API Key for service authentication")
    JWT_SECRET: str = Field(default="", description="JWT secret key (min 32 chars)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="JWT token expiration hours")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], description="Allowed CORS origins")
    RATE_LIMIT: str = Field(default="100/minute", description="Rate limit string (e.g. 100/minute)")

    # LLM Providers
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI model name")
    GOOGLE_API_KEY: str = Field(default="", description="Google API key")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro", description="Gemini model name")
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API key")
    DEEPSEEK_MODEL: str = Field(default="deepseek-v4-flash", description="DeepSeek model name")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com", description="DeepSeek API base URL")
    LLM_FALLBACK_ORDER: List[str] = Field(default=["openai", "deepseek", "gemini"], description="Fallback order for LLM providers")
    LLM_MAX_RETRIES: int = Field(default=3, description="Max retries for LLM calls")
    LLM_TIMEOUT: float = Field(default=30.0, description="LLM request timeout in seconds")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://aiworkforce:password@localhost:5432/ai_workforce",
        description="Database connection URL (asyncpg)",
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="Pool recycle seconds")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Redis max connections")

    # Voice & Media (TTS)
    TTS_PROVIDER: str = Field(default="openai", description="TTS provider")
    TTS_VOICE: str = Field(default="alloy", description="TTS voice")
    TTS_MODEL: str = Field(default="tts-1", description="TTS model")
    TTS_SPEED: float = Field(default=1.0, ge=0.25, le=4.0, description="TTS speed")
    TTS_LANGUAGE: str = Field(default="th", description="TTS language")
    MOVIES_DIR: str = Field(default="./movies", description="Movies output directory")

    # Monitoring
    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Logging format (json|text)")

    # Director AI
    DIRECTOR_AI_ENABLED: bool = Field(default=True, description="Enable DirectorAI")
    KNOWLEDGE_DIR: str = Field(default="./knowledge/director-ai", description="Knowledge base directory")

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("APP_DEBUG"):
            return v or "dev-secret-min-32-chars-long-ok"
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters in production")
        return v

    @field_validator("API_KEY")
    @classmethod
    def validate_api_key(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("APP_DEBUG"):
            return v or "dev-api-key-change-in-production"
        if len(v) < 16:
            raise ValueError("API_KEY must be at least 16 characters in production")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("LLM_FALLBACK_ORDER", mode="before")
    @classmethod
    def parse_fallback_order(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        return v


settings = Settings()
