.PHONY: install test lint format clean run build deploy

# Variables
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
MYPY = $(VENV)/bin/mypy
BLACK = $(VENV)/bin/black
ISORT = $(VENV)/bin/isort

# Default target
all: install

# Set up development environment
setup: venv install

# Create virtual environment
venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Install dependencies
install: venv
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

# Run tests
test:
	$(PYTEST) tests/ -v --cov=wikidata_mcp --cov-report=term-missing

# Run linter
lint:
	$(BLACK) --check wikidata_mcp tests
	$(ISORT) --check-only wikidata_mcp tests
	$(MYPY) wikidata_mcp tests

# Format code
format:
	$(BLACK) wikidata_mcp tests
	$(ISORT) wikidata_mcp tests

# Run the application
run:
	$(PYTHON) -m wikidata_mcp.api

# Build Docker image
build:
	docker build -t wikidata-mcp .

# Run in Docker
run-docker: build
	docker run -p 8000:8000 --env-file .env wikidata-mcp

# Run with docker-compose for development
dev:
	docker-compose up --build

# Clean up
clean:
	rm -rf $(VENV)
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '*.swp' -delete
	find . -type f -name '*.swo' -delete

# Help
help:
	@echo "Available targets:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run linter"
	@echo "  format     Format code"
	@echo "  run        Run the application"
	@echo "  build      Build Docker image"
	@echo "  run-docker Run in Docker"
	@echo "  dev        Run with docker-compose for development"
	@echo "  clean      Clean up"

.DEFAULT_GOAL := help
