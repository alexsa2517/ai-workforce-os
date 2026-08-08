# AI Workforce OS - API Documentation

## Authentication

### API Key
All requests (except health) require `X-API-Key` header.

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/agents/
```

### JWT Token
For user-specific operations:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/auth/me
```

## Endpoints

### Health
- `GET /api/v1/health/` - Full health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/metrics` - Prometheus metrics

### Chat
- `POST /api/v1/chat/` - Send message (with fallback)
- `POST /api/v1/chat/stream` - Stream response
- `GET /api/v1/chat/history/{session_id}` - Get history
- `GET /api/v1/chat/providers` - List providers

### Agents
- `GET /api/v1/agents/` - List agents
- `POST /api/v1/agents/` - Create agent
- `GET /api/v1/agents/{agent_id}` - Get agent
- `PUT /api/v1/agents/{agent_id}` - Update agent
- `DELETE /api/v1/agents/{agent_id}` - Delete agent
- `GET /api/v1/agents/{agent_id}/tasks` - List tasks
- `POST /api/v1/agents/{agent_id}/tasks` - Create task

### Auth
- `POST /api/v1/auth/login` - Get JWT token
- `GET /api/v1/auth/me` - Get current user
