# Makefile for Project Automation

.PHONY: install lint type-check test build all clean

# Variables
PACKAGE_NAME = scrapegraphai
TEST_DIR = tests

# Default target
all: lint type-check test

# Install project dependencies
install:
	uv sync
	uv run pre-commit install

# Linting and Formatting Checks
lint:
	uv run ruff check $(PACKAGE_NAME) $(TEST_DIR)
	uv run black --check $(PACKAGE_NAME) $(TEST_DIR)
	uv run isort --check-only $(PACKAGE_NAME) $(TEST_DIR)

# Type Checking with MyPy
type-check:
	uv run mypy $(PACKAGE_NAME) $(TEST_DIR)

# Run Tests with Coverage
test:
	uv run pytest --cov=$(PACKAGE_NAME) --cov-report=xml $(TEST_DIR)/

# Run Pre-Commit Hooks
pre-commit:
	uv run pre-commit run --all-files

# Clean Up Generated Files
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .uv/
	rm -rf .venv/

# Build the Package
build:
	uv build --no-sources
