"""
Helper Functions - Common utilities used across the application
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    uid = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}_{uid}"
    return uid


def generate_timestamp() -> str:
    """Generate ISO format timestamp."""
    return datetime.now(timezone.utc).isoformat()


def hash_content(content: str) -> str:
    """
    Generate SHA256 hash of content.

    Args:
        content: String to hash

    Returns:
        Hex digest string
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback default.

    Args:
        data: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON object or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum character length
        suffix: Suffix to append when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_input(text: str) -> str:
    """
    Basic input sanitization.

    Args:
        text: Raw input text

    Returns:
        Sanitized text
    """
    # Remove null bytes and control characters
    text = text.replace("\x00", "")
    text = text.strip()
    return text
