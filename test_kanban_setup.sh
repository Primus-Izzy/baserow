#!/bin/bash

# Test setup script for Kanban view backend
echo "Setting up test environment for Kanban view backend..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker to run tests."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose to run tests."
    exit 1
fi

DOCKER_COMPOSE="docker-compose"
if docker compose version &> /dev/null; then
  DOCKER_COMPOSE="docker compose"
fi

echo "Using Docker Compose command: $DOCKER_COMPOSE"

# Set environment variables for testing
export UID=$(id -u)
export GID=$(id -g)
export MIGRATE_ON_STARTUP="true"
export BASEROW_TRIGGER_SYNC_TEMPLATES_AFTER_MIGRATION="false"
export REDIS_PASSWORD=baserow
export DATABASE_PASSWORD=baserow
export SECRET_KEY=baserow
export BASEROW_DEPLOYMENT_ENV="test-$USER"

echo "Starting test database and Redis..."

# Start only the database and Redis for testing
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml up -d db redis

echo "Waiting for database to be ready..."
sleep 10

echo "Building backend test image..."
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml build backend

echo "Running Kanban view tests..."

# Run the specific Kanban tests
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml run --rm backend python -m pytest tests/baserow/contrib/database/views/test_kanban_view.py -v

echo "Test run completed!"

# Clean up
echo "Cleaning up test environment..."
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml down

echo "Test environment cleanup completed."