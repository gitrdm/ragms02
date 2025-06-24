# RAG LLM Interface Service & File-Watcher Sidecar

## Overview
This project provides a local microservice and file-watcher sidecar for enhanced, context-aware LLM responses. It supports project/tag isolation, hybrid ingestion (full and incremental), robust API design, LLM routing, and is extensible for future multi-user or production scenarios.

## Key Features
- **REST API:** Versioned, OpenAPI-documented endpoints for ingestion, querying, admin, and health.
- **File-Watcher Sidecar:** Monitors file changes using Watchdog, batching and sending events to the API.
- **Hybrid Ingestion:** Supports both full project loads and incremental updates.
- **Project/Tag Isolation:** Uses EUIDs (ULID) for robust multi-project and tag support.
- **Vector Database:** SQLite with vector extension for local/solo use, abstracted for future migration.
- **LLM Routing:** Configurable routing to local (Ollama) or cloud (Gemini, etc.) LLMs, per-query or global.
- **Security & Observability:** Local-first defaults, with optional authentication, structured logging, and metrics.
- **Development Practices:** PEP8, type hints, literate docstrings, Sphinx docs, CI, and clear contribution guidelines.

## Documentation
- [System Design Document (SDD)](docs/design/file-watcher-sdd.md)
- [OpenAPI Specification](openapi.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Architecture Decision Records (ADRs)](docs/adr/)

## Quick Start
1. Clone the repo and review the [SDD](docs/design/file-watcher-sdd.md).
2. Install dependencies (see Makefile or setup script).
3. Configure via YAML or environment variables.
4. Run the file-watcher sidecar and API service.
5. Use the OpenAPI docs or Swagger UI to explore the API.

## Development Environment & Dependency Management

This project uses [pyproject.toml](https://packaging.python.org/en/latest/tutorials/packaging-projects/) as the single source of truth for Python dependencies and supports both pip and conda workflows.

- **Editable Installs:**
  - Install in development mode with: `pip install -e .`
- **Dependency Management:**
  - All dependencies are declared in `pyproject.toml`.
  - To generate `requirements.txt` for CI or pip users, use:
    - With Poetry: `poetry export --format=requirements.txt --output=requirements.txt --without-hashes`
    - With PDM: `pdm export -o requirements.txt`
- **Conda Support:**
  - Use `environment.yml` to create a conda environment with Python and system dependencies:
    - `conda env create -f environment.yml`
    - Then activate and install the package: `conda activate <env-name>` and `pip install -e .`
- **Best Practice:**
  - Do not manually edit `requirements.txt`; always generate it from `pyproject.toml` to ensure consistency.

See CONTRIBUTING.md for more details on development workflow.

## Out of Scope
- UI or front-end client applications.
- Distributed (multi-node) deployment; this version is for local or single-node use.

---

For full requirements, see the [SDD](docs/design/file-watcher-sdd.md) and [openapi.yaml](openapi.yaml).