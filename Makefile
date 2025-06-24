# Makefile for RAG LLM Interface Service & File-Watcher Sidecar

.PHONY: help install dev test lint format run api docs clean

help:
	@echo "Available targets:"
	@echo "  install   - Install all dependencies using Poetry"
	@echo "  dev       - Install dev dependencies and pre-commit hooks"
	@echo "  test      - Run all tests with pytest"
	@echo "  lint      - Run code linting with flake8"
	@echo "  format    - Format code with black"
	@echo "  run       - Run the FastAPI app (uvicorn)"
	@echo "  api       - Show OpenAPI docs (Swagger UI)"
	@echo "  docs      - Build Sphinx documentation"
	@echo "  clean     - Remove build/test artifacts"

install:
	poetry install

dev:
	poetry install --with dev
	pre-commit install || true

test:
	poetry run pytest --maxfail=1 --disable-warnings -v

lint:
	poetry run flake8 src/ tests/

format:
	poetry run black src/ tests/

run:
	poetry run uvicorn ragms02.main:app --reload --host 0.0.0.0 --port 8000

api:
	@echo "Open http://localhost:8000/docs for Swagger UI"

clean:
	rm -rf .pytest_cache .mypy_cache dist build htmlcov .coverage

docs:
	poetry run sphinx-build -b html docs docs/_build/html
