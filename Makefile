# AI Workforce OS - Makefile
.PHONY: help install dev test lint format migrate db-reset docker-build docker-up docker-down clean

# Default target
help:
	@echo "AI Workforce OS - Available commands:"
	@echo "  make install      - Install backend dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make migrate      - Run database migrations"
	@echo "  make db-reset     - Reset database"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start all services with Docker"
	@echo "  make docker-down  - Stop all services"
	@echo "  make clean        - Clean generated files"

install:
	cd backend && pip install -r requirements.txt

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && pytest ../tests/ -v --asyncio-mode=auto

lint:
	cd backend && ruff check app/ && mypy app/

format:
	cd backend && black app/ && isort app/

migrate:
	cd backend && alembic upgrade head

db-reset:
	cd backend && alembic downgrade base && alembic upgrade head

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
