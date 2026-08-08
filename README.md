# AI Workforce OS (Improved)

Production-ready Operating System for AI Employees.

## ✨ Improvements

- 🎬 **Video Generation**: Full 5-phase AI video production workflow
- 🔒 **Security**: API Key + JWT auth, restricted CORS, rate limiting
- ⚡ **Performance**: Async PostgreSQL, Redis caching, connection pooling
- 🔄 **Resilience**: LLM fallback chain with retry + backoff
- 📊 **Monitoring**: Prometheus metrics, structured logging
- 🗄️ **Persistence**: Database-backed agents, chat history, cost tracking
- 🐳 **DevOps**: Multi-stage Dockerfile, health checks, docker-compose

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo>
cd ai-workforce-os-improved

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start with Docker
make docker-up

# 4. Check health
curl http://localhost:8000/api/v1/health/ready
```

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/          # Config, schemas, brain, logging
│   │   ├── database/      # Async SQLAlchemy models
│   │   ├── middleware/    # Auth, error handling, rate limiting
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # LLM factory, cache, monitoring
│   │   ├── auth/          # JWT utilities
│   │   └── utils/         # Helpers
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── monitoring/
    └── prometheus.yml
```

## 🔐 Security Checklist

- [ ] Change `API_KEY` in production (min 16 chars)
- [ ] Change `JWT_SECRET` in production (min 32 chars)
- [ ] Set `APP_DEBUG=false` in production
- [ ] Configure `CORS_ORIGINS` to your domain only
- [ ] Use HTTPS in production
- [ ] Enable firewall rules
- [ ] Rotate API keys regularly

## 📊 Monitoring

```bash
# Start with monitoring stack
docker-compose --profile monitoring up -d

# Access Prometheus: http://localhost:9090
# Access Grafana: http://localhost:3001 (admin/admin)
```

## 🧪 Testing

```bash
make test
```


## 🎬 Video Generation

ระบบสร้างวิดีโอด้วย AI แบบ End-to-End:

```bash
# 1. สร้างโปรเจกต์
curl -X POST http://localhost:8000/api/v1/video/projects \
  -H "X-API-Key: your-key" \
  -d '{"title":"My Video","duration_target":60}'

# 2. กำหนดสไตล์ + รัน pipeline
curl -X POST http://localhost:8000/api/v1/video/projects/vid_xxx/run-pipeline \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "style_spec": {
      "sub_genre": "Cyberpunk anime",
      "rendering_line": "2D digital painting",
      "color_lighting": "Neon, dark backgrounds",
      "detail_density": "Highly detailed"
    },
    "bgm_source": "separate",
    "bgm_properties": {
      "genre_style": "Electronic",
      "bpm": 120,
      "core_instrumentation": ["synth", "bass"]
    }
  }'
```

อ่านเพิ่มเติม: [docs/VIDEO_GENERATION.md](docs/VIDEO_GENERATION.md)

## 📝 API Usage

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Chat with fallback
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","provider":"openai"}'

# Stream response
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","provider":"openai"}'
```

## 📄 License

MIT
