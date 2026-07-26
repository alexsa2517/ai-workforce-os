# AI Workforce OS - Makefile
# Usage: make <target>

.PHONY: help run test lint build clean dev install migrate db-reset setup

# Default target
help:
	@echo "AI Workforce OS - Available commands:"
	@echo ""
	@echo "  make setup       - Initial project setup (install dependencies)"
	@echo "  make run         - Run the backend server"
	@echo "  make dev         - Run backend with auto-reload (development mode)"
	@echo "  make test        - Run all tests"
	@echo "  make lint        - Run code linting"
	@echo "  make format      - Format code with black"
	@echo "  make build       - Build Docker images"
	@echo "  make build-push  - Build and push Docker images"
	@echo "  make db-migrate  - Run database migrations"
	@echo "  make db-reset    - Reset database (drop and recreate)"
	@echo "  make db-upgrade  - Upgrade database to latest migration"
	@echo "  make docker-up   - Start all services with docker-compose"
	@echo "  make docker-down - Stop all services"
	@echo "  make docker-logs - View service logs"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make install     - Install all dependencies"

# Setup
setup: install db-migrate
	@echo "Setup complete!"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Dependencies installed!"

# Run backend
run:
	@echo "Starting backend server..."
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Development mode
dev:
	@echo "Starting backend in development mode (auto-reload)..."
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Tests
test:
	@echo "Running tests..."
	cd backend && python -m pytest ../tests/ -v --tb=short

# Linting
lint:
	@echo "Running linters..."
	cd backend && python -m ruff check app/ --fix
	cd frontend && npx eslint src/ --fix 2>/dev/null || true

# Format code
format:
	@echo "Formatting code..."
	cd backend && python -m black app/ tests/
	cd backend && python -m isort app/ tests/

# Docker
build:
	@echo "Building Docker images..."
	docker-compose build

build-push: build
	@echo "Pushing Docker images..."
	docker-compose push

docker-up:
	@echo "Starting services..."
	docker-compose up -d

docker-down:
	@echo "Stopping services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
db-migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	cd backend && rm -f ai_workforce.db && alembic upgrade head

db-upgrade:
	cd backend && alembic upgrade head

# Clean
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/dist frontend/.vite 2>/dev/null || true
	rm -rf .coverage htmlcov 2>/dev/null || true
	@echo "Clean complete!"

# Frontend
frontend-dev:
	@echo "Starting frontend dev server..."
	cd frontend && npm run dev

frontend-build:
	@echo "Building frontend..."
	cd frontend && npm run build
