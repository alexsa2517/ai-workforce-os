"""
Pydantic Schemas - API Request/Response Models

Defines data validation and serialization models for all API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


# ============================================
# Enums
# ============================================

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"


class AgentStatus(str, Enum):
    """Agent status values."""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(str, Enum):
    """Task status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================
# Chat Schemas
# ============================================

class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider")
    model: Optional[str] = Field(default=None, description="Specific model to use")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=128000)


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    provider: LLMProvider
    model: str
    response: str
    usage: Dict[str, int] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Agent Schemas
# ============================================

class AgentInfo(BaseModel):
    """Agent information schema."""
    agent_id: str
    name: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None


class AgentTask(BaseModel):
    """Task assignment to an agent."""
    task_id: str = Field(default_factory=lambda: f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    agent_id: str
    task_type: str
    description: str
    priority: int = Field(default=1, ge=1, le=5)
    parameters: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING


class TaskResult(BaseModel):
    """Result of a completed task."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None


# ============================================
# Director AI Schemas
# ============================================

class SceneRequest(BaseModel):
    """Request to create a scene."""
    character: Optional[str] = Field(default="linhfeng", description="Character name")
    world: Optional[str] = Field(default="ancient-world", description="World name")
    episode: Optional[str] = Field(default="ep001", description="Episode name")
    scene_index: Optional[int] = Field(default=0, ge=0, description="Scene index")


class SceneResponse(BaseModel):
    """Response from scene creation."""
    episode: str
    scene: str
    prompt: str


class CharacterInfo(BaseModel):
    """Character information schema."""
    name: str
    role: str
    appearance: Dict[str, Any] = Field(default_factory=dict)
    voice: Dict[str, Any] = Field(default_factory=dict)
    costume: Dict[str, Any] = Field(default_factory=dict)


class WorldInfo(BaseModel):
    """World information schema."""
    name: str
    description: str
    atmosphere: Optional[str] = None
    time_period: Optional[str] = None


class EpisodeInfo(BaseModel):
    """Episode information schema."""
    title: str
    scenes: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None


# ============================================
# Health & Status Schemas
# ============================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ============================================
# Database Schemas
# ============================================

class DBConfig(BaseModel):
    """Database configuration schema."""
    url: str
    pool_size: int = 5
    max_overflow: int = 10
