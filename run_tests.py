#!/usr/bin/env python3
"""
Comprehensive test suite for AI Workforce OS backend.
Tests all major components after fixes.
"""
import sys
import os

sys.path.insert(0, '/home/ubuntu/ai-workforce-os/backend')
sys.path.insert(0, '/home/ubuntu/ai-workforce-os')

passed = 0
failed = 0
errors = []

def test(name, func):
    global passed, failed
    try:
        func()
        passed += 1
        print(f"  PASS - {name}")
    except Exception as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"  FAIL - {name}: {e}")


print("=" * 60)
print("AI Workforce OS - Backend Tests")
print("=" * 60)

# Test 1: Config
print("\nTest 1: Configuration")
def test_config():
    from app.core.config import settings, get_settings
    assert settings.APP_NAME == "AI Workforce OS"
    assert settings.APP_VERSION == "0.2.0"
    assert hasattr(settings, "JWT_SECRET")
    assert hasattr(settings, "DEEPSEEK_API_KEY")
    assert hasattr(settings, "LIP_SYNC_PROVIDER")
    assert hasattr(settings, "MOVIES_DIR")
    assert hasattr(settings, "TTS_SPEED")
    assert hasattr(settings, "TTS_LANGUAGE")
    assert hasattr(settings, "DEEPGRAM_API_KEY")
    assert hasattr(settings, "D_ID_API_KEY")
    assert hasattr(settings, "HEDRA_API_KEY")
    assert hasattr(settings, "SCENES_PER_EPISODE")
    assert hasattr(settings, "MAX_PARALLEL_JOBS")
    assert hasattr(settings, "CHARACTER_FILE")
    assert hasattr(settings, "WORLD_FILE")
    assert hasattr(settings, "BACKGROUND_MUSIC_PATH")
    assert hasattr(settings, "SUBTITLE_FONT")
    s = get_settings()
    assert s is settings
test("Config fields and get_settings", test_config)

# Test 2: Database session
print("\nTest 2: Database Session")
def test_db_session():
    from database.session import Base, get_db, init_db, engine
    assert engine is not None
    assert hasattr(Base, "metadata")
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass
test("Database session and engine", test_db_session)

# Test 3: Database models
print("\nTest 3: Database Models")
def test_models():
    from database.models import AIAgent, AITask, ChatSession, ChatMessage
    assert AIAgent.__tablename__ == "ai_agents"
    assert AITask.__tablename__ == "ai_tasks"
    assert ChatSession.__tablename__ == "chat_sessions"
    assert ChatMessage.__tablename__ == "chat_messages"
    agent = AIAgent(agent_id="test1", name="Test", role="Test")
    assert agent.agent_id == "test1"
    task = AITask(task_id="t1", agent_id="test1", task_type="test", description="desc")
    assert task.task_id == "t1"
test("All models and instantiation", test_models)

# Test 4: LLM Factory (without actual API calls)
print("\nTest 4: LLM Factory")
def test_llm_factory():
    from app.services.llm.factory import LLMFactory
    LLMFactory.clear_cache()
    
    # Test invalid provider
    try:
        LLMFactory.get("invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test factory class attributes
    assert "openai" in LLMFactory.__dict__ or hasattr(LLMFactory, "get")
    
    # Test clear_cache
    LLMFactory.clear_cache()
    assert len(LLMFactory._instances) == 0
test("LLM factory validation and cache", test_llm_factory)

# Test 5: JWT Utils
print("\nTest 5: JWT Utilities")
def test_jwt():
    from app.auth.jwt_utils import create_access_token, decode_access_token, TokenPayload
    token = create_access_token({"sub": "test_user", "role": "admin"})
    assert token is not None
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.sub == "test_user"
    assert payload.role == "admin"
    invalid = decode_access_token("invalid_token")
    assert invalid is None
    from datetime import timedelta
    expired = create_access_token({"sub": "expired"}, expires_delta=timedelta(seconds=-1))
    result = decode_access_token(expired)
    assert result is None
test("JWT create, decode, invalid, expired", test_jwt)

# Test 6: Voice Service
print("\nTest 6: Voice Service")
def test_voice():
    from app.services.voice_service import VoiceService
    vs = VoiceService()
    assert vs.provider == "openai"
    assert vs.speed == 1.0
    assert vs.language == "th"
    voices = vs.get_available_voices()
    assert len(voices) == 6
    assert voices[0]["name"] == "alloy"
test("Voice service init and voices", test_voice)

# Test 7: Prompt Engine
print("\nTest 7: Prompt Engine")
def test_prompt_engine():
    from app.agents.director_ai.prompt_engine import PromptEngine
    pe = PromptEngine()
    char = {
        "name": "linhfeng", "english_name": "Lin Feng",
        "appearance": {
            "face": {"description": "handsome"},
            "hair": {"color": "black", "style": "long"},
        },
        "costume": {"main_outfit": "robe"},
        "voice": {"description": "deep voice"},
        "basic_information": {"gender": "male"},
    }
    world = {
        "name": "Ancient World", "era": "ancient",
        "description": "An ancient world",
        "locations": [{"name": "Temple"}],
    }
    scene = {
        "title": "Test Scene", "location": "Temple",
        "action": "walking", "emotion": "calm", "time": "morning",
    }
    prompt = pe.create_scene_prompt(char, world, scene)
    assert "linhfeng" in prompt
    assert "Temple" in prompt
    assert "walking" in prompt
    char_prompt = pe.create_character_prompt(char, "happy")
    assert "Lin Feng" in char_prompt
    world_prompt = pe.create_world_prompt(world)
    assert "Ancient World" in world_prompt
    emotion_prompt = pe.create_emotion_prompt("happy", "intense")
    assert "warm smile" in emotion_prompt
    dialogue_prompt = pe.create_dialogue_prompt(char, "Hello world")
    assert "linhfeng" in dialogue_prompt
test("Scene, character, world, emotion, dialogue prompts", test_prompt_engine)

# Test 8: Character Memory
print("\nTest 8: Character Memory")
def test_character_memory():
    from app.agents.director_ai.character_memory import CharacterMemory
    cm = CharacterMemory()
    cm.add_character("hero", {"name": "Hero", "role": "Protagonist"})
    assert cm.get_character("hero") is not None
    assert "hero" in cm.list_characters()
    cm.add_conversation("hero", "Hello", "user")
    cm.add_conversation("hero", "Hi there", "assistant")
    convos = cm.get_conversations("hero")
    assert len(convos) == 2
    ctx = cm.get_context("hero")
    assert "Hero" in ctx
    assert cm.remove_character("hero") == True
    assert cm.get_character("hero") is None
    assert cm.remove_character("nonexistent") == False
test("Add, get, converse, context, remove", test_character_memory)

# Test 9: Director AI
print("\nTest 9: Director AI")
def test_director():
    from app.agents.director_ai.director import DirectorAI
    director = DirectorAI()
    content = director.list_available_content()
    assert "characters" in content
    assert "worlds" in content
    assert "episodes" in content
    assert "linhfeng" in content["characters"]
test("Director AI initialization and listing", test_director)

# Test 10: Monitoring Service
print("\nTest 10: Monitoring Service")
def test_monitoring():
    from monitoring.monitoring_service import metrics
    # Reset counters for clean test
    metrics.counters.clear()
    metrics.gauges.clear()
    metrics.histograms.clear()
    metrics.increment_counter("test_reqs")
    metrics.increment_counter("test_reqs", 5)
    all_m = metrics.get_all()
    assert all_m["counters"]["test_reqs"] == 6
    metrics.set_gauge("test_gauge", 42.5)
    all_m = metrics.get_all()
    assert all_m["gauges"]["test_gauge"] == 42.5
    metrics.observe_histogram("test_hist", 1.5)
    metrics.observe_histogram("test_hist", 2.5)
    all_m = metrics.get_all()
    assert all_m["histograms"]["test_hist"]["count"] == 2
    assert all_m["histograms"]["test_hist"]["avg"] == 2.0
    prom = metrics.get_prometheus_format()
    assert "test_reqs" in prom
test("Counter, gauge, histogram, prometheus format", test_monitoring)

# Test 11: Core Schemas
print("\nTest 11: Core Schemas")
def test_schemas():
    from app.core.schemas import (
        ChatRequest, ChatResponse, HealthResponse,
        AgentInfo, AgentStatus, AgentTask, TaskStatus,
        SceneRequest, SceneResponse, CharacterInfo,
        WorldInfo, EpisodeInfo
    )
    from datetime import datetime, timezone
    req = ChatRequest(message="test", provider="openai")
    assert req.message == "test"
    assert req.temperature == 0.7
    resp = ChatResponse(
        provider="openai", model="gpt-4", response="hi",
        usage={}, timestamp=datetime.now(timezone.utc),
    )
    assert resp.provider == "openai"
    health = HealthResponse(
        status="healthy", version="1.0",
        services={}, timestamp=datetime.now(timezone.utc),
    )
    assert health.status == "healthy"
    agent = AgentInfo(
        agent_id="test", name="Test", role="Test",
        status=AgentStatus.IDLE, capabilities=[],
        created_at=datetime.now(timezone.utc),
    )
    assert agent.status == "idle"
test("All Pydantic schemas", test_schemas)

# Test 12: Database Init
print("\nTest 12: Database Init")
def test_db_init():
    from database.session import init_db
    init_db()
    from database.session import engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "ai_agents" in tables
    assert "ai_tasks" in tables
    assert "chat_sessions" in tables
    assert "chat_messages" in tables
test("Database tables created", test_db_init)

# Test 13: Brain Service
print("\nTest 13: Brain Service")
def test_brain():
    from brain.brain_service import BrainService
    brain = BrainService()
    brain.register_provider("openai", "mock")
    brain.register_provider("gemini", "mock")
    assert "openai" in brain.get_available_providers()
    assert "gemini" in brain.get_available_providers()
test("Brain service register and list", test_brain)

# Test 14: Alembic migration
print("\nTest 14: Alembic Migration File")
def test_alembic():
    import importlib.util
    spec = importlib.util.spec_from_file_location("migration", "/home/ubuntu/ai-workforce-os/backend/alembic/versions/001_initial.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.revision == "001"
    assert mod.down_revision is None
test("Alembic migration file structure", test_alembic)

# Summary
print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
if errors:
    print("\nFailed tests:")
    for name, err in errors:
        print(f"  - {name}: {err}")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
