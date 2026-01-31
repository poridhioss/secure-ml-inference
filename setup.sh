#!/bin/bash

# Setup script for FastAPI Load Balanced API
# This script sets up the entire project

set -e

echo "=========================================="
echo "FastAPI Load Balanced API - Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}! .env file already exists${NC}"
fi
echo ""

# Build Docker images
echo -e "${BLUE}Building Docker images...${NC}"
docker compose build
echo -e "${GREEN}✓ Docker images built successfully${NC}"
echo ""

# Start services
echo -e "${BLUE}Starting services...${NC}"
docker compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 10

# Check if PostgreSQL is ready
echo -e "${BLUE}Checking PostgreSQL...${NC}"
until docker exec lab9_postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Initialize database
echo -e "${BLUE}Initializing database...${NC}"
docker exec lab9_fastapi1 python init_db.py
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Display service status
echo -e "${BLUE}Service Status:${NC}"
docker compose ps
echo ""

# Test health endpoints
echo -e "${BLUE}Testing health endpoints...${NC}"
sleep 2

NGINX_HEALTH=$(curl -s http://localhost/nginx-health)
API_HEALTH=$(curl -s http://localhost/health | jq -r '.status')

if [ "$API_HEALTH" == "healthy" ]; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
fi
echo ""

# Display summary
echo -e "${GREEN}=========================================="
echo "Setup completed successfully!"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo "  API Endpoint:      http://localhost"
echo "  API Documentation: http://localhost/docs"
echo "  Nginx Health:      http://localhost/nginx-health"
echo "  API Health:        http://localhost/health"
echo ""
echo -e "${BLUE}Sample Users:${NC}"
echo "  Admin User:"
echo "    Username: admin"
echo "    Password: admin123"
echo ""
echo "  Test User:"
echo "    Username: testuser"
echo "    Password: test123"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Run 'make test' to test the API"
echo "  2. Visit http://localhost/docs for interactive API documentation"
echo "  3. Run 'make logs' to view application logs"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  make help   - Show all available commands"
echo "  make logs   - View logs"
echo "  make down   - Stop all services"
echo "  make clean  - Remove all containers and volumes"
echo ""