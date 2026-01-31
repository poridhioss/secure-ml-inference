.PHONY: help build up down logs restart clean init-db test

help:
	@echo "FastAPI Load Balanced API - Available Commands"
	@echo "================================================"
	@echo "make build      - Build Docker images"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make logs       - View logs from all services"
	@echo "make restart    - Restart all services"
	@echo "make clean      - Remove all containers and volumes"
	@echo "make init-db    - Initialize database with sample data"
	@echo "make test       - Run API tests"
	@echo "make shell      - Open shell in fastapi1 container"
	@echo "make ps         - Show running containers"

build:
	@echo "Building Docker images..."
	docker compose build

up:
	@echo "Starting all services..."
	docker compose up -d
	@echo "Waiting for services to be ready..."
	sleep 5
	@echo "Services started successfully!"
	@echo "Access the API at: http://localhost"
	@echo "API Documentation: http://localhost/docs"

down:
	@echo "Stopping all services..."
	docker compose down

logs:
	docker compose logs -f

restart:
	@echo "Restarting all services..."
	docker compose restart

clean:
	@echo "Removing all containers, volumes, and images..."
	docker compose down -v
	@echo "Cleanup completed!"

init-db:
	@echo "Initializing database with sample data..."
	docker exec lab9_fastapi1 python init_db.py
	@echo "Database initialized!"
	@echo ""
	@echo "Sample users created:"
	@echo "  Admin - username: admin, password: admin123"
	@echo "  Test  - username: testuser, password: test123"

test:
	@echo "Running API tests..."
	chmod +x test_api.sh
	./test_api.sh

shell:
	@echo "Opening shell in fastapi1 container..."
	docker exec -it lab9_fastapi1 /bin/bash

ps:
	docker compose ps