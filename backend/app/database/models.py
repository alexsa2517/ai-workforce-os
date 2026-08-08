"""
Database Models - SQLAlchemy ORM (Async + PostgreSQL)
Includes Video Generation System
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, JSON, DateTime, 
    ForeignKey, Index, func, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# ============================================
# Core Models
# ============================================

class AIAgent(Base):
    """AI Agent record - persisted in database."""
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="idle", index=True)
    capabilities = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)

    tasks = relationship("AITask", back_populates="agent", cascade="all, delete-orphan", lazy="selectin")
    conversations = relationship("Conversation", back_populates="agent", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_agent_status", "status"),
        Index("idx_agent_created", "created_at"),
    )


class AITask(Base):
    """AI Task record."""
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    agent_id = Column(String(255), ForeignKey("ai_agents.agent_id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    status = Column(String(50), default="pending", index=True)
    parameters = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    agent = relationship("AIAgent", back_populates="tasks")

    __table_args__ = (
        Index("idx_task_status_agent", "status", "agent_id"),
        Index("idx_task_created", "created_at"),
    )


class Conversation(Base):
    """Conversation history - persists chat context."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(255), ForeignKey("ai_agents.agent_id", ondelete="SET NULL"), nullable=True, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("AIAgent", back_populates="conversations")

    __table_args__ = (
        Index("idx_conv_session", "session_id", "created_at"),
        Index("idx_conv_agent", "agent_id", "created_at"),
    )


class ChatSession(Base):
    """Chat session metadata."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    agent_id = Column(String(255), ForeignKey("ai_agents.agent_id", ondelete="SET NULL"), nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)


class LLMUsageLog(Base):
    """Track LLM usage for cost monitoring."""
    __tablename__ = "llm_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    request_duration_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_llm_usage_provider", "provider", "created_at"),
        Index("idx_llm_usage_date", "created_at"),
    )


class SystemMetric(Base):
    """System metrics for monitoring."""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    labels = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_metric_name_time", "metric_name", "created_at"),
    )


# ============================================
# Video Generation Models
# ============================================

class VideoProject(Base):
    """Video project - top level container for AI video production."""
    __tablename__ = "video_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Phase 1: Requirements
    goal = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    duration_target = Column(Integer, nullable=True)  # seconds
    aspect_ratio = Column(String(20), default="16:9")  # 16:9 or 9:16
    visual_style = Column(Text, nullable=True)
    language = Column(String(50), default="th")

    # Phase 2: Global Definitions
    style_spec = Column(JSON, default=dict)  # sub_genre, rendering, color_lighting, detail_density
    voice_profiles = Column(JSON, default=dict)
    bgm_source = Column(String(50), default="separate")  # embedded, separate, none
    bgm_properties = Column(JSON, default=dict)  # genre, bpm, key, instrumentation

    # Status
    status = Column(String(50), default="draft", index=True)  # draft, planning, generating, assembling, completed, failed
    current_phase = Column(String(50), default="initial")  # initial, global_def, clip_plan, ref_images, execution, done
    progress_percent = Column(Integer, default=0)

    # Output
    output_url = Column(String(1000), nullable=True)
    output_path = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    clips = relationship("VideoClip", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    assets = relationship("VideoAsset", back_populates="project", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_video_project_status", "status"),
        Index("idx_video_project_created", "created_at"),
    )


class VideoClip(Base):
    """Individual video clip within a project."""
    __tablename__ = "video_clips"

    id = Column(Integer, primary_key=True, index=True)
    clip_id = Column(String(255), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("video_projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ordering
    sequence_number = Column(Integer, nullable=False, default=0)

    # Phase 3: Clip Planning
    narrative_purpose = Column(String(50), nullable=True)  # establish, develop, climax, resolve, transition, supplementary
    pacing = Column(String(20), default="moderate")  # slow, moderate, fast
    scene = Column(Text, nullable=True)
    content_action = Column(Text, nullable=True)
    transition_description = Column(Text, nullable=True)
    target_duration = Column(Float, default=5.0)  # seconds
    camera_movement = Column(String(50), default="static")
    first_keyframe_framing = Column(Text, nullable=True)
    first_keyframe_visible_content = Column(Text, nullable=True)
    inter_clip_boundary = Column(String(20), default="scene_cut")  # continuous, scene_cut
    first_keyframe_reuse = Column(Boolean, default=False)

    # Audio
    on_screen_dialogue = Column(JSON, nullable=True)  # {name: text, language: "th"}
    sound_effects = Column(JSON, nullable=True)
    bgm_cue = Column(JSON, nullable=True)
    narration_cue = Column(Text, nullable=True)
    narration_budget = Column(Float, nullable=True)

    # Status
    status = Column(String(50), default="pending", index=True)  # pending, keyframe_ready, generating, completed, failed

    # Output
    video_url = Column(String(1000), nullable=True)
    video_path = Column(String(1000), nullable=True)
    actual_duration = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("VideoProject", back_populates="clips")
    assets = relationship("VideoAsset", back_populates="clip", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_video_clip_project", "project_id", "sequence_number"),
        Index("idx_video_clip_status", "status"),
    )


class VideoAsset(Base):
    """Assets for video generation (reference images, keyframes, audio files)."""
    __tablename__ = "video_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(255), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("video_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    clip_id = Column(Integer, ForeignKey("video_clips.id", ondelete="CASCADE"), nullable=True, index=True)

    asset_type = Column(String(50), nullable=False, index=True)  # reference_image, keyframe, video, audio_tts, audio_bgm, audio_sfx, final_video
    asset_role = Column(String(50), nullable=True)  # primary_ref, face_closeup, full_body, first_keyframe, etc.

    # Storage
    url = Column(String(1000), nullable=True)
    local_path = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    # Metadata
    prompt_used = Column(Text, nullable=True)
    generation_params = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("VideoProject", back_populates="assets")
    clip = relationship("VideoClip", back_populates="assets")

    __table_args__ = (
        Index("idx_video_asset_project", "project_id", "asset_type"),
        Index("idx_video_asset_clip", "clip_id", "asset_type"),
    )
