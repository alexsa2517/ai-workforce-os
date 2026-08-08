"""
Pydantic Schemas - API Request/Response Models (Improved)
Includes Video Generation System
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


# ============================================
# Enums
# ============================================

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoProjectStatus(str, Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    GENERATING = "generating"
    ASSEMBLING = "assembling"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoClipStatus(str, Enum):
    PENDING = "pending"
    KEYFRAME_READY = "keyframe_ready"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoPhase(str, Enum):
    INITIAL = "initial"
    GLOBAL_DEF = "global_def"
    CLIP_PLAN = "clip_plan"
    REF_IMAGES = "ref_images"
    EXECUTION = "execution"
    DONE = "done"


class AssetType(str, Enum):
    REFERENCE_IMAGE = "reference_image"
    KEYFRAME = "keyframe"
    VIDEO = "video"
    AUDIO_TTS = "audio_tts"
    AUDIO_BGM = "audio_bgm"
    AUDIO_SFX = "audio_sfx"
    FINAL_VIDEO = "final_video"


class BgmSource(str, Enum):
    EMBEDDED = "embedded"
    SEPARATE = "separate"
    NONE = "none"


class NarrativePurpose(str, Enum):
    ESTABLISH = "establish"
    DEVELOP = "develop"
    CLIMAX = "climax"
    RESOLVE = "resolve"
    TRANSITION = "transition"
    SUPPLEMENTARY = "supplementary"


class Pacing(str, Enum):
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"


class CameraMovement(str, Enum):
    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    DOLLY = "dolly"
    ZOOM = "zoom"
    CRANE = "crane"
    ARC = "arc"
    HANDHELD = "handheld"


class InterClipBoundary(str, Enum):
    CONTINUOUS = "continuous"
    SCENE_CUT = "scene_cut"


# ============================================
# Chat Schemas
# ============================================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider")
    model: Optional[str] = Field(default=None, description="Specific model to use")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=128000)
    stream: bool = Field(default=False, description="Enable streaming response")
    session_id: Optional[str] = Field(default=None, description="Conversation session ID")


class ChatResponse(BaseModel):
    provider: LLMProvider
    model: str
    response: str
    usage: Dict[str, int] = Field(default_factory=dict)
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatStreamChunk(BaseModel):
    provider: LLMProvider
    model: str
    chunk: str
    session_id: str
    is_final: bool = False


# ============================================
# Agent Schemas
# ============================================

class AgentInfo(BaseModel):
    agent_id: str
    name: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    config: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=255, description="Unique agent identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Agent display name")
    role: str = Field(..., min_length=1, max_length=255, description="Agent role")
    description: Optional[str] = Field(default=None, max_length=2000)
    capabilities: List[str] = Field(default_factory=list)
    config: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    role: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


# ============================================
# Task Schemas
# ============================================

class TaskInfo(BaseModel):
    task_id: str
    agent_id: str
    task_type: str
    description: str
    priority: int = Field(default=1, ge=1, le=10)
    status: TaskStatus = TaskStatus.PENDING
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    task_id: str = Field(..., min_length=1, max_length=255)
    agent_id: str = Field(..., min_length=1, max_length=255)
    task_type: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=5000)
    priority: int = Field(default=1, ge=1, le=10)
    parameters: Optional[Dict[str, Any]] = None


# ============================================
# Health Schemas
# ============================================

class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# Auth Schemas
# ============================================

class TokenRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================
# Scene Schemas (DirectorAI)
# ============================================

class SceneRequest(BaseModel):
    character: str = Field(default="linhfeng", description="Character name")
    world: str = Field(default="ancient-world", description="World name")
    episode: str = Field(default="ep001", description="Episode name")
    scene_index: int = Field(default=0, ge=0, description="Scene index")


class SceneResponse(BaseModel):
    episode: str
    scene_index: int
    scene_prompt: str
    dialogue: Optional[str] = None
    characters: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


# ============================================
# Conversation History
# ============================================

class ConversationMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    tokens_used: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[ConversationMessage]
    total_tokens: int = 0


# ============================================
# VIDEO GENERATION SCHEMAS
# ============================================

class StyleSpec(BaseModel):
    """Visual style specification for video project."""
    sub_genre: str = Field(..., description="e.g. 'Makoto Shinkai anime', 'cyberpunk noir'")
    rendering_line: str = Field(..., description="e.g. '2D hand-drawn with thick outlines'")
    color_lighting: str = Field(..., description="e.g. 'High saturation neon, dark backgrounds'")
    detail_density: str = Field(..., description="e.g. 'Highly detailed backgrounds'")


class VoiceProfile(BaseModel):
    """Voice profile for narration or on-screen dialogue."""
    name: str
    gender: str = Field(default="female", description="female, male, neutral")
    tone: str = Field(default="warm", description="warm, professional, energetic, calm")
    pace: str = Field(default="moderate", description="slow, moderate, fast")
    language: str = Field(default="th")


class BgmProperties(BaseModel):
    """Background music properties."""
    genre_style: str
    bpm: int = Field(default=120, ge=60, le=200)
    key_scale: str = Field(default="C major")
    core_instrumentation: List[str] = Field(default_factory=list)
    soundscape: str = Field(default="clean")
    production_quality: str = Field(default="studio")


class VideoProjectCreate(BaseModel):
    """Request to create a new video project."""
    title: str = Field(..., min_length=1, max_length=500, description="Project title")
    description: Optional[str] = Field(default=None, max_length=5000)
    goal: Optional[str] = Field(default=None, description="Video goal and purpose")
    target_audience: Optional[str] = Field(default=None)
    duration_target: Optional[int] = Field(default=60, ge=10, le=300, description="Target duration in seconds")
    aspect_ratio: str = Field(default="16:9", pattern="^(16:9|9:16)$")
    visual_style: Optional[str] = Field(default=None, description="Overall visual style description")
    language: str = Field(default="th")


class VideoProjectUpdate(BaseModel):
    """Update video project requirements."""
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    goal: Optional[str] = None
    target_audience: Optional[str] = None
    duration_target: Optional[int] = Field(default=None, ge=10, le=300)
    visual_style: Optional[str] = None
    language: Optional[str] = None


class VideoProjectGlobalDef(BaseModel):
    """Phase 2: Global definitions for video project."""
    style_spec: StyleSpec
    voice_profiles: Dict[str, VoiceProfile] = Field(default_factory=dict)
    bgm_source: BgmSource = BgmSource.SEPARATE
    bgm_properties: Optional[BgmProperties] = None
    recurring_elements: Optional[List[Dict[str, Any]]] = None


class VideoClipPlan(BaseModel):
    """Phase 3: Individual clip plan."""
    sequence_number: int = Field(..., ge=0)
    narrative_purpose: NarrativePurpose = NarrativePurpose.ESTABLISH
    pacing: Pacing = Pacing.MODERATE
    scene: str = Field(..., description="Environment description")
    content_action: str = Field(..., description="Subject + action + trajectory")
    transition_description: str = Field(..., min_length=50, description="Detailed transition, 2-4 sentences minimum")
    target_duration: float = Field(default=5.0, ge=3.0, le=10.0)
    camera_movement: CameraMovement = CameraMovement.STATIC
    first_keyframe_framing: str = Field(..., description="Shot size + angle + composition")
    first_keyframe_visible_content: str = Field(..., description="What is visible in the frame")
    inter_clip_boundary: InterClipBoundary = InterClipBoundary.SCENE_CUT
    first_keyframe_reuse: bool = False
    on_screen_dialogue: Optional[Dict[str, str]] = None
    sound_effects: Optional[List[str]] = None
    bgm_cue: Optional[Dict[str, Any]] = None
    narration_cue: Optional[str] = None
    narration_budget: Optional[float] = None


class VideoClipResponse(BaseModel):
    """Video clip response."""
    clip_id: str
    sequence_number: int
    narrative_purpose: str
    pacing: str
    scene: str
    content_action: str
    transition_description: str
    target_duration: float
    camera_movement: str
    status: str
    video_url: Optional[str] = None
    actual_duration: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoAssetInfo(BaseModel):
    """Video asset information."""
    asset_id: str
    asset_type: str
    asset_role: Optional[str] = None
    url: Optional[str] = None
    local_path: Optional[str] = None
    prompt_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoProjectResponse(BaseModel):
    """Video project response."""
    project_id: str
    title: str
    description: Optional[str] = None
    status: str
    current_phase: str
    progress_percent: int
    aspect_ratio: str
    duration_target: Optional[int] = None
    output_url: Optional[str] = None
    style_spec: Optional[Dict[str, Any]] = None
    voice_profiles: Optional[Dict[str, Any]] = None
    bgm_source: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    clips: List[VideoClipResponse] = Field(default_factory=list)
    assets: List[VideoAssetInfo] = Field(default_factory=list)

    class Config:
        from_attributes = True


class VideoGenerateRequest(BaseModel):
    """Request to start video generation."""
    project_id: str
    provider: LLMProvider = LLMProvider.OPENAI
    auto_execute: bool = Field(default=True, description="Auto execute all phases")


class VideoGenerationStatus(BaseModel):
    """Video generation status response."""
    project_id: str
    status: str
    current_phase: str
    progress_percent: int
    message: str
    clips_completed: int
    clips_total: int
    estimated_time_remaining: Optional[int] = None  # seconds


class VideoNarrationSegment(BaseModel):
    """Narration segment spanning one or more clips."""
    segment_id: str
    text: str
    voice_profile: str
    start_clip_sequence: int
    end_clip_sequence: int
    estimated_duration: float
    ssml: Optional[str] = None


class BgmEmotionalArcRow(BaseModel):
    """Single row in BGM emotional arc blueprint."""
    time_segment: str  # e.g. "[00:00-00:16]"
    mood_emotion: str
    arrangement_state: str  # sparse, moderate, dense, full
    density_brightness: Optional[str] = None
    active_instruments: Optional[List[str]] = None


class BgmBlueprint(BaseModel):
    """BGM emotional arc blueprint."""
    total_duration: int
    bpm: int
    key_scale: str
    segments: List[BgmEmotionalArcRow]
    global_directives: str = "Instrumental only, no vocals"
