"""
Tests for utility helper functions
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.utils.helpers import (
    generate_id,
    generate_timestamp,
    hash_content,
    safe_json_loads,
    truncate_text,
    sanitize_input,
)


def test_generate_id():
    """Test unique ID generation."""
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2
    assert len(id1) == 8


def test_generate_id_with_prefix():
    """Test ID generation with prefix."""
    id_with_prefix = generate_id("task")
    assert id_with_prefix.startswith("task_")


def test_generate_timestamp():
    """Test timestamp generation."""
    ts = generate_timestamp()
    assert "T" in ts  # ISO format has T separator


def test_hash_content():
    """Test content hashing."""
    hash1 = hash_content("hello")
    hash2 = hash_content("hello")
    hash3 = hash_content("world")
    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64  # SHA256 hex digest


def test_safe_json_loads():
    """Test safe JSON parsing."""
    result = safe_json_loads('{"key": "value"}')
    assert result == {"key": "value"}

    result = safe_json_loads("invalid json", default={})
    assert result == {}


def test_truncate_text():
    """Test text truncation."""
    short_text = "hello"
    assert truncate_text(short_text) == "hello"

    long_text = "a" * 1000
    truncated = truncate_text(long_text, max_length=100)
    assert len(truncated) == 100
    assert truncated.endswith("...")


def test_sanitize_input():
    """Test input sanitization."""
    assert sanitize_input("  hello  ") == "hello"
    assert sanitize_input("test\x00data") == "testdata"
