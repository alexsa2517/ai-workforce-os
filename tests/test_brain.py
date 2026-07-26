"""
Tests for the AI Brain module
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.brain import Brain


def test_brain_init():
    """Test Brain initialization."""
    brain = Brain(provider="openai")
    assert brain.provider == "openai"
    assert brain.context == []
    assert len(brain.system_prompt) > 0


def test_brain_clear_context():
    """Test context clearing."""
    brain = Brain()
    brain.context.append({"role": "user", "content": "test"})
    brain.clear_context()
    assert brain.context == []


def test_brain_set_personality():
    """Test personality setting."""
    brain = Brain()
    brain.set_personality("You are a helpful assistant.")
    assert "helpful assistant" in brain.system_prompt


def test_brain_set_provider():
    """Test provider switching."""
    brain = Brain(provider="openai")
    brain.set_provider("gemini")
    assert brain.provider == "gemini"


def test_brain_context_summary():
    """Test context summary generation."""
    brain = Brain()
    summary = brain.get_context_summary()
    assert "total_messages" in summary
    assert "provider" in summary
    assert summary["total_messages"] == 0


def test_brain_analyze_task():
    """Test task analysis."""
    brain = Brain()
    result = brain.analyze_task("Create a report for the meeting")
    assert "detected_task" in result
    assert "priority" in result
    assert result["priority"] >= 1
