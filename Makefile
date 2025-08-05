.PHONY: help build up down restart logs clean shell

# Default target: Show help
help:
	@echo "🚀 Notification Bot - Docker Commands"
	@echo "======================================"
	@echo ""
	@echo "📋 Available commands:"
	@echo "  make build          - Build or rebuild services"
	@echo "  make up             - Start all services in the background"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs from all services"
	@echo "  make logs-app       - View logs from the API service"
	@echo "  make logs-worker    - View logs from the Worker service"
	@echo "  make clean          - Stop and remove containers, networks, and volumes"
	@echo "  make shell          - Access the shell of the app container"
	@echo ""
	@echo "🌐 Quick Start:"
	@echo "  make up"
	@echo ""
	@echo "🔗 URLs:"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "🚀 Starting services..."
	docker-compose up -d --build
	@echo ""
	@echo "✅ Services started successfully!"
	@echo "📊 Check status with: docker-compose ps"
	@echo "🔗 API Docs available at: http://localhost:8000/docs"

# Stop all services
down:
	@echo "🛑 Stopping services..."
	docker-compose down

# Restart all services
restart: down up

# View logs from all services
logs:
	@echo "📝 Tailing logs from all services..."
	docker-compose logs -f

# View logs from the app service
logs-app:
	@echo "📝 Tailing logs from the app service..."
	docker-compose logs -f app

# View logs from the worker service
logs-worker:
	@echo "📝 Tailing logs from the worker service..."
	docker-compose logs -f worker

# Clean up everything (containers, volumes, networks)
clean:
	@echo "🧹 Cleaning up containers, networks, and volumes..."
	docker-compose down -v --remove-orphans
	@echo "✅ Cleanup completed!"

# Access the app container shell
shell:
	@echo "💻 Accessing the app container shell..."
	docker-compose exec app /bin/sh 