# =============================================================================
# RH Hume Project - Makefile
# Contested Logistics Intelligence Platform
# =============================================================================

.PHONY: help setup up down restart logs ps build test lint format clean

# Auto-detect container runtime (Podman or Docker)
CONTAINER_RUNTIME := $(shell command -v podman 2> /dev/null && echo "podman" || echo "docker")
COMPOSE_CMD := $(shell command -v podman-compose 2> /dev/null && echo "podman-compose" || echo "$(CONTAINER_RUNTIME) compose")

# Docker compose file location
COMPOSE = $(COMPOSE_CMD) -f docker/docker-compose.yml

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# HELP
# =============================================================================

help:  ## Show this help message
	@echo ""
	@echo "RH Hume Project - Contested Logistics Intelligence Platform"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# SETUP
# =============================================================================

setup:  ## Initial project setup
	@echo "Setting up RH Hume Project..."
	@if [ ! -f docker/.env ]; then \
		cp docker/.env.example docker/.env; \
		echo "Created docker/.env - please edit with your API keys"; \
	fi
	@pip install -e ".[dev]" 2>/dev/null || pip install -r requirements-dev.txt 2>/dev/null || echo "Install dependencies manually"
	@if command -v pre-commit >/dev/null 2>&1; then pre-commit install; fi
	@mkdir -p data/{raw,processed,presentation,synthetic}
	@mkdir -p logs
	@echo "Setup complete!"

check-runtime:  ## Show detected container runtime
	@echo "Container runtime: $(CONTAINER_RUNTIME)"
	@echo "Compose command: $(COMPOSE_CMD)"

verify-env:  ## Verify development environment
	@./scripts/verify_env.sh

# =============================================================================
# DOCKER SERVICES
# =============================================================================

up:  ## Start all services
	$(COMPOSE) up -d
	@echo ""
	@echo "Services starting..."
	@echo "  Kafka UI:      http://localhost:8080"
	@echo "  Neo4j Browser: http://localhost:7474"
	@echo "  Agent API:     http://localhost:8000"
	@echo ""

up-logs:  ## Start all services with logs attached
	$(COMPOSE) up

down:  ## Stop all services
	$(COMPOSE) down

down-v:  ## Stop all services and remove volumes (DESTRUCTIVE)
	@echo "This will delete all data. Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	$(COMPOSE) down -v

restart:  ## Restart all services
	$(COMPOSE) restart

logs:  ## View logs (usage: make logs service=api)
ifdef service
	$(COMPOSE) logs -f $(service)
else
	$(COMPOSE) logs -f
endif

ps:  ## Show running services
	$(COMPOSE) ps

build:  ## Build Docker images
	$(COMPOSE) build

rebuild:  ## Rebuild and restart services
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

# Individual services
up-infra:  ## Start infrastructure only (Kafka, Neo4j)
	$(COMPOSE) up -d zookeeper kafka kafka-ui neo4j

up-api:  ## Start API service
	$(COMPOSE) up -d api

up-consumers:  ## Start Kafka consumers
	$(COMPOSE) --profile consumers up -d consumers

# =============================================================================
# INITIALIZATION
# =============================================================================

init:  ## Initialize Kafka topics and Neo4j indexes
	@echo "Initializing Kafka topics..."
	$(COMPOSE) --profile init run --rm kafka-init
	@echo "Initializing Neo4j indexes..."
	$(COMPOSE) --profile init run --rm neo4j-init
	@echo "Initialization complete!"

init-kafka:  ## Initialize Kafka topics only
	$(COMPOSE) --profile init run --rm kafka-init

init-neo4j:  ## Initialize Neo4j indexes only
	$(COMPOSE) --profile init run --rm neo4j-init

# =============================================================================
# JOBS
# =============================================================================

generate-data:  ## Generate synthetic demo data
	$(COMPOSE) --profile jobs run --rm jobs python -m jobs.runner generate_data

run-pipeline:  ## Run full ETL pipeline
	$(COMPOSE) --profile jobs run --rm jobs python -m jobs.runner full_pipeline

run-job:  ## Run specific job (usage: make run-job JOB=etl)
ifndef JOB
	@echo "Usage: make run-job JOB=<job_name>"
	@echo "Available jobs: generate_data, etl, load_neo4j, hume_batch, embeddings, aggregations, qlik_presentation, narratives, full_pipeline"
else
	$(COMPOSE) --profile jobs run --rm jobs python -m jobs.runner $(JOB)
endif

job-help:  ## Show available jobs
	$(COMPOSE) --profile jobs run --rm jobs python -m jobs.runner --help

# =============================================================================
# DEMO
# =============================================================================

reset-demo:  ## Reset demo to clean state
	@echo "Resetting demo environment..."
	@./scripts/reset_demo.sh

load-snapshot:  ## Load data snapshot (usage: make load-snapshot SNAPSHOT=disrupted)
ifndef SNAPSHOT
	@echo "Usage: make load-snapshot SNAPSHOT=<snapshot_name>"
	@echo "Available snapshots: baseline, disrupted, recovery"
else
	$(COMPOSE) --profile jobs run --rm jobs python -m jobs.runner load_snapshot --snapshot $(SNAPSHOT)
endif

check-health:  ## Check service health
	@echo "=== Service Health Check ==="
	@echo ""
	@echo -n "API:      " && curl -sf http://localhost:8000/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','ERROR'))" 2>/dev/null || echo "DOWN"
	@echo -n "Neo4j:    " && curl -sf http://localhost:7474 >/dev/null && echo "UP" || echo "DOWN"
	@echo -n "Kafka UI: " && curl -sf http://localhost:8080 >/dev/null && echo "UP" || echo "DOWN"
	@echo ""

demo-ready:  ## Full demo preparation
	@echo "Preparing demo environment..."
	make down-v 2>/dev/null || true
	make up
	@echo "Waiting for services to start..."
	@sleep 30
	make init
	make generate-data
	make run-pipeline
	make check-health
	@echo ""
	@echo "Demo ready!"

# =============================================================================
# DEVELOPMENT
# =============================================================================

shell-api:  ## Open shell in API container
	$(COMPOSE) exec api /bin/bash

shell-jobs:  ## Open shell in jobs container
	$(COMPOSE) --profile jobs run --rm jobs /bin/bash

shell-neo4j:  ## Open Neo4j cypher-shell
	$(COMPOSE) exec neo4j cypher-shell -u neo4j -p $${NEO4J_PASSWORD:-password}

python-shell:  ## Open Python shell with project loaded
	$(COMPOSE) --profile jobs run --rm jobs python -c "from src import *; import IPython; IPython.embed()"

# Local development (without Docker)
dev-install:  ## Install dependencies locally
	pip install -e ".[dev]"

dev-api:  ## Run API locally (requires local dependencies)
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

dev-consumers:  ## Run consumers locally
	python -m src.kafka.run_consumers --consumer all

# =============================================================================
# TESTING
# =============================================================================

test:  ## Run all tests
	pytest tests/ -v

test-unit:  ## Run unit tests only
	pytest tests/unit/ -v

test-integration:  ## Run integration tests
	pytest tests/integration/ -v

test-golden:  ## Run golden test cases (agent quality)
	pytest tests/golden/ -v

coverage:  ## Run tests with coverage report
	pytest tests/ --cov=src --cov=jobs --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# =============================================================================
# CODE QUALITY
# =============================================================================

lint:  ## Run linters
	ruff check src/ jobs/ tests/
	mypy src/ --ignore-missing-imports

format:  ## Format code
	ruff format src/ jobs/ tests/
	ruff check --fix src/ jobs/ tests/

typecheck:  ## Run type checking
	mypy src/ --ignore-missing-imports

pre-commit:  ## Run pre-commit hooks
	pre-commit run --all-files

# =============================================================================
# CLEANUP
# =============================================================================

clean:  ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ dist/ build/
	@echo "Cleaned!"

clean-data:  ## Clean data directories (DESTRUCTIVE)
	@echo "This will delete all data files. Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	rm -rf data/raw/* data/processed/* data/presentation/* data/synthetic/*
	@echo "Data cleaned!"

clean-all: clean down-v clean-data  ## Full cleanup (DESTRUCTIVE)
	@echo "Full cleanup complete!"

# =============================================================================
# DOCUMENTATION
# =============================================================================

docs:  ## Build documentation
	@echo "Documentation build not yet configured"

docs-serve:  ## Serve documentation locally
	@echo "Documentation server not yet configured"

# =============================================================================
# UTILITIES
# =============================================================================

neo4j-browser:  ## Open Neo4j browser URL
	@echo "Opening http://localhost:7474"
	@which xdg-open >/dev/null 2>&1 && xdg-open http://localhost:7474 || echo "Open http://localhost:7474 in your browser"

kafka-ui:  ## Open Kafka UI URL
	@echo "Opening http://localhost:8080"
	@which xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8080 || echo "Open http://localhost:8080 in your browser"

api-docs:  ## Open API docs URL
	@echo "Opening http://localhost:8000/docs"
	@which xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8000/docs || echo "Open http://localhost:8000/docs in your browser"

urls:  ## Show all service URLs
	@echo ""
	@echo "Service URLs:"
	@echo "  Kafka UI:      http://localhost:8080"
	@echo "  Neo4j Browser: http://localhost:7474"
	@echo "  Agent API:     http://localhost:8000"
	@echo "  API Docs:      http://localhost:8000/docs"
	@echo ""
