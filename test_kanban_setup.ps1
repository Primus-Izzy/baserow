# Test setup script for Kanban view backend
Write-Host "Setting up test environment for Kanban view backend..." -ForegroundColor Green

# Check if Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed. Please install Docker to run tests." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
$dockerCompose = "docker-compose"
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    try {
        docker compose version | Out-Null
        $dockerCompose = "docker compose"
    } catch {
        # Fall back to docker-compose
    }
}

Write-Host "Using Docker Compose command: $dockerCompose" -ForegroundColor Yellow

# Set environment variables for testing
$env:MIGRATE_ON_STARTUP = "true"
$env:BASEROW_TRIGGER_SYNC_TEMPLATES_AFTER_MIGRATION = "false"
$env:REDIS_PASSWORD = "baserow"
$env:DATABASE_PASSWORD = "baserow"
$env:SECRET_KEY = "baserow"
$env:BASEROW_DEPLOYMENT_ENV = "test-$env:USERNAME"

Write-Host "Starting test database and Redis..." -ForegroundColor Yellow

# Start only the database and Redis for testing
if ($dockerCompose -eq "docker compose") {
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db redis
} else {
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d db redis
}

Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Building backend test image..." -ForegroundColor Yellow
if ($dockerCompose -eq "docker compose") {
    docker compose -f docker-compose.yml -f docker-compose.dev.yml build backend
} else {
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml build backend
}

Write-Host "Running Kanban view tests..." -ForegroundColor Green

# Run the specific Kanban tests
if ($dockerCompose -eq "docker compose") {
    docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend python -m pytest tests/baserow/contrib/database/views/test_kanban_view.py -v
} else {
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend python -m pytest tests/baserow/contrib/database/views/test_kanban_view.py -v
}

Write-Host "Test run completed!" -ForegroundColor Green

# Clean up
Write-Host "Cleaning up test environment..." -ForegroundColor Yellow
if ($dockerCompose -eq "docker compose") {
    docker compose -f docker-compose.yml -f docker-compose.dev.yml down
} else {
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
}

Write-Host "Test environment cleanup completed." -ForegroundColor Green