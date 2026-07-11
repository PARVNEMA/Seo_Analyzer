# =============================================================================
# FastAPI Template - Makefile
# =============================================================================

.PHONY: help install run test lint format migrate migration docker-up docker-down docker-logs clean

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Development
# -----------------------------------------------------------------------------
install: ## Install all dependencies (including dev)
	pip install --upgrade pip setuptools wheel
	pip install -r requirements-dev.txt
	pre-commit install

run: ## Run the development server with hot-reload
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------
test: ## Run tests with coverage
	pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov -v

test-fast: ## Run tests without coverage (faster)
	pytest -x -q

# -----------------------------------------------------------------------------
# Code Quality
# -----------------------------------------------------------------------------
lint: ## Run all linters (ruff, black check, mypy)
	ruff check app/ tests/
	black --check app/ tests/
	mypy app/

format: ## Auto-format code with ruff and black
	ruff check --fix app/ tests/
	black app/ tests/

# -----------------------------------------------------------------------------
# Database Migrations
# -----------------------------------------------------------------------------
migrate: ## Apply all pending migrations
	alembic upgrade head

migration: ## Create a new migration (usage: make migration m="migration message")
	alembic revision --autogenerate -m "$(m)"

downgrade: ## Downgrade one migration
	alembic downgrade -1

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------
docker-up: ## Start all services in detached mode
	docker-compose up -d --build

docker-down: ## Stop and remove all containers
	docker-compose down

docker-logs: ## Tail logs from all services
	docker-compose logs -f

docker-clean: ## Stop containers and remove volumes
	docker-compose down -v --remove-orphans

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
clean: ## Remove cache files and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
