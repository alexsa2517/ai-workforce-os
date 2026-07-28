# AI Workforce OS - Code Audit Report

## Critical Bugs

### 1. Config: .env loading path is wrong
- **File**: `backend/app/core/config.py`
- **Issue**: Loads `.env` from `Path(__file__).resolve().parents[3] / ".env"` which resolves to the repo root, but `.env.example` and `.env.guide` are in `backend/` directory. The `backend/.env.example` is the canonical location.
- **Impact**: Settings may not load API keys correctly.

### 2. Config: Missing many settings from .env.example
- **File**: `backend/app/core/config.py`
- **Issue**: `backend/.env.example` defines many more settings (Deepgram, LipSync, Movie Pipeline, Character, Video Assembly) that are NOT in the Settings class.
- **Missing**: DEEPGRAM_API_KEY, DEEPGRAM_MODEL, TTS_SPEED, TTS_LANGUAGE, LIP_SYNC_PROVIDER, LIP_SYNC_RESOLUTION, D_ID_BASE_URL, HEDRA_BASE_URL, MOVIES_DIR, SCENES_PER_EPISODE, MAX_PARALLEL_JOBS, CHARACTER_FILE, WORLD_FILE, BACKGROUND_MUSIC_PATH, SUBTITLE_FONT, JWT_SECRET, D_ID_API_KEY, HEDRA_API_KEY

### 3. Config: CORS_ORIGINS as string in .env vs List[str] in config
- **File**: `backend/app/core/config.py`
- **Issue**: In `.env.example`, CORS_ORIGINS is `["http://localhost:3000","http://localhost:5173"]` (a string), but the config field is `List[str]`. Pydantic may not parse this correctly.

### 4. Config: Config class is deprecated in Pydantic v2
- **File**: `backend/app/core/config.py`
- **Issue**: Uses `class Config:` inner class which is deprecated in Pydantic v2. Should use `model_config = SettingsConfigDict(...)`.

### 5. main.py: Logger used before setup_logging
- **File**: `backend/app/main.py`
- **Issue**: `logger = logging.getLogger("ai_workforce.main")` is used inside `lifespan()` before `setup_logging()` is called. Should be after setup_logging.

### 6. auth/jwt_utils.py: JWT_SECRET default is insecure
- **File**: `backend/app/auth/jwt_utils.py`
- **Issue**: Default JWT_SECRET is hardcoded: `"ai-workforce-os-dev-secret-change-in-production"`. Should be required in .env.

### 7. database/session.py: SQLAlchemy pool_size with SQLite
- **File**: `backend/app/core/session.py` (imported as `database/session.py`)
- **Issue**: `pool_size` and `max_overflow` are set for the engine but SQLite doesn't support connection pooling. This will cause warnings/errors.

### 8. database/models.py: Duplicate Base class
- **File**: `database/models.py` and `database/session.py`
- **Issue**: `database/models.py` defines its own `Base = declarative_base()` but `database/session.py` also defines `Base(DeclarativeBase)`. Two different Base classes means tables won't be created properly.

### 9. Alembic env.py: Uses wrong Base
- **File**: `backend/alembic/env.py`
- **Issue**: Alembic uses `database.models.Base` but the main.py imports `database.session.init_db()` which uses `database.session.Base`. Mismatch between Alembic and runtime.

### 10. LLM Services: No connection timeout/error handling
- **File**: `backend/app/services/llm/openai.py`, `gemini.py`, `deepseek.py`
- **Issue**: No timeout, no retry, no error handling for API calls.

### 11. LLM Services: No structured output support
- **File**: All LLM clients
- **Issue**: Only basic `generate(prompt)` method. No support for system prompts, temperature, max_tokens parameters that are defined in ChatRequest schema.

### 12. Factory: Does not use config settings
- **File**: `backend/app/services/llm/factory.py`
- **Issue**: Factory creates clients but doesn't pass model names or API keys from settings. Each client loads its own env vars independently.

### 13. Voice Service: Imports from relative path incorrectly
- **File**: `backend/app/services/llm/openai_voice.py`
- **Issue**: `from ..voice_service import VoiceService` - this relative import may fail depending on how the module is loaded.

### 14. Voice Router: Missing Pydantic model for request
- **File**: `backend/app/routers/voice.py`
- **Issue**: `text_to_speech(text: str, ...)` uses query parameters instead of request body. POST with query params is non-standard.

### 15. Chat Router: Legacy endpoint doesn't use settings
- **File**: `backend/app/main.py` (legacy chat endpoint)
- **Issue**: Legacy `/chat` endpoint creates `LLMFactory.get(request.provider)` but doesn't pass model or API key from settings.

### 16. Character Memory: Minimal implementation
- **File**: `backend/app/agents/director_ai/character_memory.py`
- **Issue**: Very basic implementation with no persistence, no methods. Just a dict wrapper.

### 17. Prompt Engine: Basic implementation
- **File**: `backend/app/agents/director_ai/prompt_engine.py`
- **Issue**: Only has `create_scene_prompt` method. Missing methods for character, world, emotion prompts.

### 18. Frontend: Missing @vitejs/plugin-react in package.json
- **File**: `frontend/package.json`
- **Issue**: `vite.config.ts` uses `react()` from `@vitejs/plugin-react` but it's not in dependencies.

### 19. Frontend: No react-router-dom
- **File**: `frontend/package.json`
- **Issue**: No routing library, uses simple state-based navigation. Functional but limiting.

### 20. Frontend: No error boundary
- **File**: `frontend/src/App.tsx`
- **Issue**: No error boundary, any crash will show blank page.

### 21. Frontend: API service hardcoded paths
- **File**: `frontend/src/services/api.ts`
- **Issue**: API paths may not match backend router prefixes exactly. Backend uses `/api/v1/health/` but frontend calls `/api/v1/health/` (with trailing slash).

### 22. Monitoring: metrics_endpoint not registered
- **File**: `backend/app/main.py`
- **Issue**: `monitoring/metrics_endpoint.py` defines a router but it's never imported or registered in `main.py`.

### 23. Movie Pipeline: No router
- **File**: `backend/app/services/pipeline/movie_pipeline.py`
- **Issue**: Movie pipeline has no API router for triggering pipeline runs.

### 24. Lip Sync: No router
- **File**: `backend/app/services/lip_sync/lip_sync_service.py`
- **Issue**: Lip sync service has no API router.

### 25. Cache: No API endpoints
- **File**: `backend/app/services/cache_service.py`
- **Issue**: Cache service exists but no API to inspect or manage cache.

### 26. Docker: .env not in Dockerfile context
- **File**: `Dockerfile`
- **Issue**: `COPY .env /app/.env 2>/dev/null || true` - the shell redirect won't work in Dockerfile COPY instruction.

### 27. Docker: CMD path wrong
- **File**: `Dockerfile`
- **Issue**: `CMD ["uvicorn", "backend.app.main:app", ...]` but the WORKDIR is `/app` and code is copied to `/app/backend/app`. Should be `app.main:app`.

### 28. Tests: Only 3 test files, low coverage
- **File**: `tests/`
- **Issue**: Only tests for brain, config, and helpers. Missing tests for routers, services, auth, agents.

### 29. Health Router: Doesn't check real service status
- **File**: `backend/app/routers/health.py`
- **Issue**: Hardcoded "healthy" for all services without actually checking them.

### 30. Alembic: No target_metadata set properly
- **File**: `backend/alembic/env.py`
- **Issue**: Need to verify target_metadata is correctly set.
