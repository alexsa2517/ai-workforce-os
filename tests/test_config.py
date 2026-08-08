"""
Configuration Tests
"""
import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_jwt_secret_validation():
    with pytest.raises(ValidationError):
        Settings(JWT_SECRET="short", APP_DEBUG=False)


def test_api_key_validation():
    with pytest.raises(ValidationError):
        Settings(API_KEY="short", APP_DEBUG=False)


def test_debug_mode_allows_weak_secrets():
    settings = Settings(JWT_SECRET="short", API_KEY="short", APP_DEBUG=True)
    assert settings.JWT_SECRET == "short"
