#!/bin/bash
set -e

echo "🚀 AI Workforce OS - Setup Script"

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required"; exit 1; }

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from example"
    echo "⚠️  Please edit .env and set your API keys!"
fi

# Create directories
mkdir -p movies logs monitoring

# Build and start
echo "🔨 Building containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d db redis

echo "⏳ Waiting for database..."
sleep 5

echo "📝 Running migrations..."
docker-compose run --rm backend alembic upgrade head

echo "🚀 Starting backend..."
docker-compose up -d backend

echo "✅ Setup complete!"
echo "📊 API: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f backend"
