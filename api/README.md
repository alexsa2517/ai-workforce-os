# API Endpoints

## Authentication
TBD - JWT authentication will be implemented in future versions.

## Endpoints

### Root
- `GET /` - Application info
- `GET /health` - Health check

### API v1

#### Chat
- `POST /api/v1/chat/` - Send chat message to AI provider

#### Health
- `GET /api/v1/health/` - System health check
- `GET /api/v1/health/ready` - Readiness check

#### Agents
- `GET /api/v1/agents/` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `POST /api/v1/agents/{agent_id}/tasks` - Assign task to agent

#### Director AI
- `POST /api/v1/agents/director/scene` - Create cinematic scene
- `GET /api/v1/agents/director/characters/{name}` - Get character info
- `GET /api/v1/agents/director/worlds/{name}` - Get world info
- `GET /api/v1/agents/director/episodes/{name}` - Get episode info

#### Voice
- `POST /api/v1/voice/tts` - Text-to-speech
- `GET /api/v1/voice/voices` - List available voices

## Documentation
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI: `/openapi.json`
