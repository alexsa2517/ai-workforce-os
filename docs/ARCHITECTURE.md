# AI Workforce OS - Architecture

## Overview

AI Workforce OS is a production-ready platform for deploying AI employees with:
- **Async PostgreSQL** database
- **Redis** caching layer
- **Multi-provider LLM** with automatic fallback
- **JWT + API Key** authentication
- **Prometheus** metrics
- **Rate limiting** protection

## Components

```
┌─────────────────┐
│   Client App    │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Nginx  │  (Reverse Proxy / SSL)
    └────┬────┘
         │
┌────────┴────────┐
│  FastAPI App    │  (Uvicorn + Workers)
│  - Rate Limit   │
│  - API Key Auth │
│  - JWT Auth     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───┴───┐  ┌──┴────┐
│PostgreSQL│  │ Redis │
│  (Async)│  │(Cache)│
└─────────┘  └───────┘
         │
    ┌────┴────┐
    │  LLM    │  (OpenAI / DeepSeek / Gemini)
    │ Fallback│
    └─────────┘
```

## Security

1. **API Key** - Required for all endpoints except health checks
2. **JWT** - User authentication for admin operations
3. **CORS** - Restricted to configured origins
4. **Rate Limiting** - Per-IP rate limits
5. **Input Validation** - Pydantic schemas with strict validation

## Database Schema

- `ai_agents` - Agent registry
- `ai_tasks` - Task queue
- `conversations` - Chat history
- `chat_sessions` - Session metadata
- `llm_usage_logs` - Cost tracking
- `system_metrics` - Monitoring data

## LLM Fallback Chain

```
Primary Provider → Retry 3x → Fallback 1 → Retry 3x → Fallback 2 → Error
```

## Deployment

```bash
# Development
make dev

# Production with Docker
make docker-up

# With monitoring stack
docker-compose --profile monitoring up -d
```
