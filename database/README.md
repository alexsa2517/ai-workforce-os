# Database

## Schema Overview

| Table | Description |
|-------|-------------|
| ai_agents | AI agent records and configurations |
| ai_tasks | Task assignments and results |
| chat_sessions | Chat session metadata |
| chat_messages | Individual chat messages |

## Configuration
- Default: SQLite (`ai_workforce.db`)
- Production: PostgreSQL (see `.env.example` for DATABASE_URL)
- Pool size: 5 connections
- Max overflow: 10 connections

## Usage
```python
from database.session import get_db, init_db
from database.models import AIAgent, AITask

# Initialize tables
init_db()
```
