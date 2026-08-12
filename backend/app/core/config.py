"""
Application Configuration
Central configuration management using environment variables.
"""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[3] / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    _backend_env = Path(__file__).resolve().parents[2] / ".env"
    if _backend_env.exists():
        load_dotenv(dotenv_path=_backend_env)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = Field(default="AI Workforce OS")
    APP_VERSION: str = Field(default="0.3.0")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)
    APP_DEBUG: bool = Field(default=False)

    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o")
    GOOGLE_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-3.1-flash-image")
    GOOGLE_IMAGE_MODEL: str = Field(default="gemini-3.1-flash-image")
    GOOGLE_VIDEO_MODEL: str = Field(default="veo-3.1-generate-preview")
    DEEPSEEK_API_KEY: str = Field(default="")
    DEEPSEEK_MODEL: str = Field(default="deepseek-v4-flash")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com")

    JWT_SECRET: str = Field(default="")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)

    DATABASE_URL: str = Field(default="sqlite:///./ai_workforce.db")
    DATABASE_POOL_SIZE: int = Field(default=5)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)

    TTS_PROVIDER: str = Field(default="openai")
    TTS_VOICE: str = Field(default="alloy")
    TTS_MODEL: str = Field(default="tts-1")
    TTS_SPEED: float = Field(default=1.0)
    TTS_LANGUAGE: str = Field(default="th")
    DEEPGRAM_API_KEY: str = Field(default="")
    DEEPGRAM_MODEL: str = Field(default="aura-asteria-en")

    LIP_SYNC_PROVIDER: str = Field(default="did")
    LIP_SYNC_RESOLUTION: str = Field(default="720p")
    D_ID_API_KEY: str = Field(default="")
    D_ID_BASE_URL: str = Field(default="https://api.d-id.com")
    HEDRA_API_KEY: str = Field(default="")
    HEDRA_BASE_URL: str = Field(default="https://api.hedra.com")

    MOVIES_DIR: str = Field(default="./movies")
    SCENES_PER_EPISODE: int = Field(default=5)
    MAX_PARALLEL_JOBS: int = Field(default=3)
    CHARACTER_FILE: str = Field(default="linhfeng.json")
    WORLD_FILE: str = Field(default="ancient-world.json")
    BACKGROUND_MUSIC_PATH: str = Field(default="")
    SUBTITLE_FONT: str = Field(default="NotoSansThai-Regular.ttf")

    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/ai_workforce.log")

    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)

    DIRECTOR_AI_ENABLED: bool = Field(default=True)
    KNOWLEDGE_BASE_PATH: str = Field(default="./knowledge/director-ai")
    REAL_MEDIA_ENABLED: bool = Field(default=False)


settings = Settings()


def get_settings() -> Settings:
    return settings
