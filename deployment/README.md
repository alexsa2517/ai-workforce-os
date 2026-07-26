# Deployment

## Docker Deployment
```bash
# Build
docker build -t ai-workforce-os:latest .

# Run
docker run -p 8000:8000 --env-file .env ai-workforce-os:latest

# Docker Compose (with database)
docker-compose up -d
```

## Manual Deployment
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Environment Variables
See `.env.example` for all required environment variables.

## Production Checklist
- [ ] Set APP_DEBUG=false
- [ ] Configure DATABASE_URL for production database
- [ ] Set all API keys (OPENAI, GOOGLE, DEEPSEEK)
- [ ] Configure CORS_ORIGINS for production domain
- [ ] Set LOG_LEVEL=WARNING
- [ ] Enable HTTPS/TLS
