"""
Utility Helpers
"""
import uuid
import re
from datetime import datetime, timezone
from typing import Optional


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def sanitize_string(text: str, max_length: int = 255) -> str:
    """Sanitize string for safe storage."""
    text = re.sub(r"[<>'"]", "", text)
    return text[:max_length]


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string."""
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat()


def estimate_tokens(text: str) -> int:
    """Roughly estimate token count (1 token ≈ 0.75 words)."""
    words = len(text.split())
    return int(words / 0.75)
