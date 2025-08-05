.PHONY: help build up down restart logs clean status shell test backup restore

# Default target
help:
	@echo "🚀 Docker Commands"
	@echo "============================================="
	@echo ""
	@echo "📋 Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make status   - Show status of all containers"
	@echo "  make shell    - Access Django shell"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make backup   - Backup database"
	@echo "  make restore  - Restore database"
	@echo ""
	@echo "🌐 Quick Start:"
	@echo "  make build && make up"
	@echo ""
	@echo "🔗 URLs:"
	@echo "  API Docs: http://localhost:8000/swagger/"
	@echo ""

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo ""
	@echo "✅ Services started successfully!"
	@echo "📖 API Documentation: http://localhost:8000/swagger/"
	@echo "🔧 Admin Panel: http://localhost:8000/admin/"
	@echo "👤 Default Admin: admin@ravid.cloud / admin123"
	@echo ""
	@echo "📊 Check status: make status"
	@echo "📝 View logs: make logs"

# Stop all services
down:
	@echo "🛑 Stopping RAVID services..."
	docker-compose down

# Restart all services
restart: down up

# View logs
logs:
	@echo "📝 Viewing logs from all services..."
	docker-compose logs -f

# Show container status
status:
	@echo "📊 Container Status:"
	@echo "==================="
	docker-compose ps
	@echo ""
	@echo "🐳 Docker Images:"
	@echo "================"
	docker images | grep ravid

# Access Django shell
shell:
	@echo "🐍 Accessing Django shell..."
	docker-compose exec web python manage.py shell

# Run tests
test:
	@echo "🧪 Running tests..."
	docker-compose exec web python manage.py test

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Database backup
backup:
	@echo "💾 Creating database backup..."
	docker-compose exec db mysqldump -u ravid_user -pravid_password ravid_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

# Database restore (usage: make restore FILE=backup_file.sql)
restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify backup file: make restore FILE=backup_file.sql"; \
		exit 1; \
	fi
	@echo "📥 Restoring database from $(FILE)..."
	docker-compose exec -T db mysql -u ravid_user -pravid_password ravid_db < $(FILE)
	@echo "✅ Database restored!"

# Development helpers
dev-logs-web:
	docker-compose logs -f web

dev-logs-celery:
	docker-compose logs -f celery

dev-logs-db:
	docker-compose logs -f db

dev-logs-redis:
	docker-compose logs -f redis

# Health check
health:
	@echo "🏥 Health Check:"
	@echo "==============="
	@echo "Web API:"
	@curl -s http://localhost:8000/api/register/ -o /dev/null && echo "✅ API is healthy" || echo "❌ API is down"
	@echo "Admin Panel:"
	@curl -s http://localhost:8000/admin/ -o /dev/null && echo "✅ Admin is healthy" || echo "❌ Admin is down"
	@echo "Swagger Docs:"
	@curl -s http://localhost:8000/swagger/ -o /dev/null && echo "✅ Swagger is healthy" || echo "❌ Swagger is down" 