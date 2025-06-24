# System Design Document: File-Watcher Sidecar and RAG LLM Interface Service

## Status

**Milestone Complete:**  
All ADRs have been finalized and incorporated. This SDD is up to date, implementation-ready, and reflects all architectural decisions regarding ingestion API, payload format, authentication, security, and deployment. No pending updates remain for this milestone.

# System Design Document: File-Watcher Sidecar and RAG LLM Interface Service

## Overview

This document describes the architecture and implementation plan for the file-watcher sidecar and its integration with the RAG LLM Interface Service. The system uses **LangChain** as the core RAG pipeline for chunking, retrieval, and LLM context assembly. LangChain enables LLM-optimized chunking, efficient similarity search, and robust context construction for LLM queries. The system monitors file changes in code repositories and document directories, supports project/tag isolation using EUIDs, and notifies the RAG LLM Interface Service for both full and incremental ingestion. The design is robust for solo/local use but is extensible for future multi-user or production scenarios, supporting hybrid ingestion, flexible API/LLM routing, and secure, observable operations.

---

## Goals

- Detect file changes (create, modify, delete, move/rename) in specified directories.
- Efficiently notify the ingestion API with only the changed/affected files.
- Support configuration for file patterns, directories, batching, and debounce intervals.
- Support project and tag isolation using EUIDs (ULID), enabling multi-project and multi-tag queries.
- Enable hybrid ingestion: full project loads and incremental updates via file-watcher.
- Provide robust, versioned RESTful API endpoints with per-query LLM routing and extensibility.
- Be extensible for future triggers (e.g., git hooks, CI/CD) and multi-user/production deployment.
- Handle operational concerns such as error handling, retries, observability, and secure configuration.

---

## Out of Scope

- Parsing/ingesting file content (handled by the RAG service).
- Full project scanning (except for initial load).
- Direct integration with git or other VCS (future work).

---

## Architecture

### Components

- **File Watcher Process:**  
  Monitors filesystem events using the Python `watchdog` library. Watchdog is cross-platform (Linux, macOS, Windows), actively maintained, and provides robust event handling for create, modify, delete, and move/rename operations. This choice enables easy integration with Python-based tools and ML workflows.
- **Event Aggregator:**  
  Batches rapid changes, applies debounce logic, and filters events according to config.
- **Change Verifier:**  
  Optionally confirms real file changes using file hash or modification time to filter out redundant events.
- **Notifier/Client:**  
  Sends notifications to the RAG ingestion API (HTTP), with authentication and retries.

### Deployment

- Runs as a sidecar process on developer machines, CI, or dedicated servers.
- Configured via environment variables or YAML/JSON config file.

---

## File Change Detection (Detailed)

### Event Source & Cross-Platform Support

- **Native OS APIs:**  
  Use platform-native file system event APIs (`inotify` on Linux, `FSEvents` on macOS, `ReadDirectoryChangesW` on Windows) for real-time, low-overhead detection.
- **Library Abstraction:**  
  Use a cross-platform abstraction library (e.g., `watchdog` for Python), ensuring maintainability and portability.
- **Fallback to Polling:**  
  If native APIs are unavailable or unreliable (e.g., network shares), fallback to periodic directory polling (e.g., every 2 seconds).

### Event Types Handled

- **Created:** New files or directories.
- **Modified:** File contents changed.
- **Deleted:** Files or directories removed.
- **Moved/Renamed:** Files or directories change name/location.
- **(Configurable) Ignore:** Symlinks, permission changes, hidden/temp files.

### Batching & Debouncing

- **Batching:**  
  Collect file system events in a configurable time window (default: 500ms).
- **Debouncing:**  
  Only process after the window has passed with no new events.
- **Benefits:**  
  - Prevent redundant work and API calls.
  - Efficiently handle event storms (e.g., git checkout, bulk editor saves).
- **Configurable Parameters:**  
  - `debounce_ms`: Duration (ms) for the batch window.
  - `batch_size`: Max events per notification.

### Change Verification

- **Rationale:**  
  Some editors and tools trigger redundant/duplicate modification events.
- **Strategy:**  
  - Maintain a lightweight cache or snapshot for each watched file:  
    `{ path, last_modified, hash (optional) }`
  - On event, compare new mtime (modification time) and/or hash to previous cache:
    - If changed, enqueue for notification and update cache.
    - If unchanged, ignore event.
  - Persist cache on disk at regular intervals and on graceful shutdown, to survive restarts.
- **Config Option:**  
  - Enable/disable hash verification (for large files, mtime alone may suffice).

### Edge Case Handling

- **Atomic Saves:**  
  Detect patterns where editors write to temp file and rename (delete + create/move).
- **Multi-step Operations:**  
  Correctly aggregate operations from git or other tools that may rapidly move, delete, and create files.
- **Symlinks, Permission Changes, Hidden Files:**  
  Filter using include/exclude patterns and config.
- **Hidden/Temp Files:**  
  Ignore via glob patterns (e.g., `.*`, `~*`, `*.swp`).

### Resource Limits & Scalability

- **Watched Paths:**  
  Limit to configured directories and file types to avoid exceeding OS limits.
- **Include/Exclude Patterns:**  
  Use glob patterns to further narrow scope and reduce overhead.

### Fallback to Polling

- **When to Fallback:**  
  - If the watcher detects that native event APIs are not available (e.g., network filesystem).
  - If the maximum number of watched files/directories is exceeded.
- **Polling Interval:**  
  Configurable (default: 2 seconds).
- **Polling Strategy:**  
  - Compare current snapshot to last-known cache for changes.

### Example Implementation Flow

1. **Startup:**  
   - Load configuration (paths, patterns, verification settings).
   - Build initial snapshot/cache of watched files.
2. **On FS Event:**  
   - Match file path against include/exclude patterns.
   - If matches, batch event with debounce.
   - Optionally, verify with mtime/hash.
   - Add to notification payload.
3. **On Batch Ready:**  
   - Send notification payload to ingestion API.
   - Update cache/snapshot for persisted state.
4. **On Shutdown:**  
   - Persist cache/snapshot to disk.

### Example Pseudocode

```python
def on_fs_event(event):
    if matches_patterns(event.path):
        if verify_change(event.path):
            add_to_batch(event)
    # batch is sent after debounce_ms

def verify_change(path):
    curr_mtime = get_mtime(path)
    curr_hash = get_hash(path) if hash_verification_enabled else None
    prev = snapshot_cache[path]
    if curr_mtime != prev.mtime or (curr_hash and curr_hash != prev.hash):
        snapshot_cache[path] = { 'mtime': curr_mtime, 'hash': curr_hash }
        return True
    return False
```

---

## Configuration Handling

- The watcher loads configuration from a YAML (or JSON) file at startup. The config file path can be specified via an environment variable (e.g., `WATCHER_CONFIG`), defaulting to `./watcher.yml` if not set.
- Any configuration key can be overridden via environment variables (e.g., `WATCHER_API_TOKEN` overrides `api.token`). Environment variables take precedence over file values.
- Secrets (API keys/tokens) should be provided via environment variables or injected at runtime—not stored in source control.
- The watcher validates configuration on startup and exits with an error if required fields are missing or invalid.
- (Optional) Support for hot-reloading configuration on SIGHUP or when the config file changes.
- Default values are provided for optional settings; required settings must be supplied.
- Example config file:

```yaml
# watcher.yml
paths:
  - ./src
  - ./docs
include:
  - '*.py'
  - '*.md'
exclude:
  - '*.log'
debounce_ms: 500
batch_size: 50
verify_hash: false
polling_interval: 2000
api:
  endpoint: 'https://rag.example.com/ingest'
  token: '${WATCHER_API_TOKEN}'
  timeout: 10
```

- Example environment variable overrides:
  - `WATCHER_API_TOKEN=supersecrettoken`
  - `WATCHER_DEBOUNCE_MS=1000`

---

## Configuration Schema

| Key                | Type    | Required | Default        | Description                                                          |
|--------------------|---------|----------|----------------|----------------------------------------------------------------------|
| paths              | list    | yes      | -              | Directories to watch                                                 |
| include            | list    | no       | `['*']`        | File patterns to include                                             |
| exclude            | list    | no       | `[]`           | File patterns to exclude                                             |
| debounce_ms        | int     | no       | `500`          | Milliseconds to batch events                                         |
| batch_size         | int     | no       | `50`           | Max files/events per API call                                        |
| verify_hash        | bool    | no       | `false`        | Enable hash-based change verification                                |
| polling_interval   | int     | no       | `2000`         | Polling interval in ms (fallback mode)                               |
| api.endpoint       | string  | yes      | -              | Ingestion API endpoint URL                                           |
| api.token          | string  | yes      | -              | Bearer token for API auth (should be provided via env var)           |
| api.timeout        | int     | no       | `10`           | API request timeout (seconds)                                        |

---

## Error Handling & Reliability

- Retries failed API calls with exponential backoff.
- Local queue/disk buffer for events if network/API is unavailable.
- Logs all changes, sends metrics for monitoring.
- Configurable alerting on persistent failures.

---

## Security

- API requests are authenticated (e.g., bearer token).
- Sensitive config (e.g., API key) not logged and not stored in source control.
- Option to restrict watcher to specific users or environments.

---

## Observability

- Logs key events: watcher start/stop, file events, API requests, failures.
- Exposes metrics: number of changes detected, notifications sent, retries, queue depth.
- Optional healthcheck endpoint.

---

## Extensibility

- Plugin system for future triggers (git hooks, CI/CD, polling).
- Pluggable event filters or preprocessors.

---

## Implementation Plan

1. **Prototype file watcher** using a cross-platform library (e.g., `watchdog` for Python).
2. **Event aggregator** with batching and debounce logic.
3. **Change verifier** for optional hash/mtime confirmation.
4. **API notifier client** with retries and authentication.
5. **Config loader** (YAML/JSON/env).
6. **Basic logging and metrics**.
7. **Integration test suite** simulating create/modify/delete scenarios.
8. Document setup and usage.

---

## Open Questions

- Final strategy for file change identity (hash vs. timestamp vs. name).
- Format of API payloads for changed files.
- Minimum/maximum supported platforms (Windows, Mac, Linux).
- Should we support running as a container out-of-the-box?

---

## References

- [openapi.yaml](../openapi.yaml) — Canonical OpenAPI (Swagger) specification for all API endpoints, schemas, and error formats.
- [ADR-0003 Ingestion Method](./0003-ingestion-method.md)
- [ADR-9999 Decision Backlog](./9999-decision-backlog.md)
- [watchdog Python project](https://github.com/gorakhargosh/watchdog)
- [RAG ingestion API docs] (TBD)

---

## API Specification

The full, authoritative API contract is defined in the OpenAPI specification:
- [openapi.yaml](../../openapi.yaml)

This file documents all endpoints, request/response schemas, authentication, and error formats. It should be kept up to date with any changes to the API or implementation.

---

## Ingestion API Endpoints and Payloads

### Endpoint: Notify File Changes
- **Method:** POST
- **Path:** `/api/v1/ingest/notify`
- **Description:** Receives batched file change notifications from the file-watcher sidecar. The API is designed to support both local and remote/server deployments by allowing for robust file identification and optional file content or storage references.

#### Request Payload (JSON)
```
{
  "project_id": "string",           // Project identifier
  "events": [
    {
      "path": "string",             // Project-root-relative file path
      "event_type": "created|modified|deleted|moved", // Type of change
      "timestamp": "ISO8601 string", // Event time (UTC)
      "uuid": "string (optional)",  // Optional: stable file UUID
      "hash": "string (optional)",  // Optional: content hash
      "content": "string (optional)", // Optional: file content (base64 or text)
      "storage_url": "string (optional)", // Optional: reference to file in shared storage
      "old_path": "string (optional)" // For moved/renamed events
    },
    // ...more events
  ]
}
```
- **Required fields:** `project_id`, `events[].path`, `events[].event_type`, `events[].timestamp`
- **Optional fields:** `events[].uuid`, `events[].hash`, `events[].content`, `events[].storage_url`, `events[].old_path`

#### Example Request
```
POST /api/v1/ingest/notify
Content-Type: application/json
Authorization: Bearer <token>

{
  "project_id": "docs-site",
  "events": [
    { "path": "docs/README.md", "event_type": "modified", "timestamp": "2025-06-24T12:34:56Z", "hash": "abc123..." },
    { "path": "src/main.py", "event_type": "created", "timestamp": "2025-06-24T12:35:01Z", "uuid": "file-uuid-xyz", "content": "..." }
  ]
}
```

#### Response
- **200 OK**: `{ "status": "success" }`
- **4xx/5xx**: Error message

---

### Endpoint: Query LLM
- **Method:** POST
- **Path:** `/api/v1/query`
- **Description:** Accepts user queries and returns LLM-augmented responses, grounded in DSL or documentation sources.

#### Request Payload (JSON)
```
{
  "query": "string",                // User's question or prompt
  "projects": ["string", ...],      // List of project IDs to search
  "context": { ... }                 // (Optional) Additional context or parameters
}
```

#### Example Request
```
POST /api/v1/query
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "How do I define a new command in the DSL?",
  "projects": ["my-dsl-project"]
}
```

#### Response
```
{
  "response": "To define a new command in your DSL, add a block like:\n\ncommand mycmd {\n  ...\n}\nSee the example in [1].",
  "sources": [
    {
      "path": "dsl/commands.dsl",
      "snippet": "command mycmd {\n  ...\n}",
      "score": 0.97
    },
    {
      "path": "docs/dsl-guide.md",
      "snippet": "You can define commands using the 'command' keyword...",
      "score": 0.88
    }
  ],
  "citations": [
    { "id": 1, "path": "dsl/commands.dsl", "offset": [38, 60] }
  ],
  "confidence": 0.92
}
```
- **Fields:**
  - `response`: The LLM’s answer, possibly including DSL code or examples.
  - `sources`: Array of supporting sources, each with `path`, `snippet`, and optional `score`.
  - `citations`: (Optional) Inline mapping of answer segments to sources.
  - `confidence`: (Optional) LLM’s confidence in the answer.
  - `error`: (Optional) For error or fallback messages.

---

## Typical Response Formats

Below are recommended response formats for the main API endpoints:

- **/api/v1/ingest/notify**
  ```json
  { "status": "success" }
  // On error:
  { "status": "error", "error": "Description of the problem" }
  ```
- **/api/v1/query**
  ```json
  {
    "response": "LLM answer...",
    "sources": [
      { "path": "docs/file.dsl", "snippet": "...", "score": 0.95 }
    ],
    "citations": [
      { "id": 1, "path": "docs/file.dsl", "offset": [38, 60] }
    ],
    "confidence": 0.92,
    "error": null
  }
  ```
- **/api/v1/admin/reset**
  ```json
  { "status": "reset", "message": "Database/index has been cleared." }
  // On error:
  { "status": "error", "error": "Description of the problem" }
  ```
- **/api/v1/admin/reindex**
  ```json
  { "status": "reindexing", "message": "Reindexing started for project X." }
  ```
- **/api/v1/health**
  ```json
  { "status": "ok", "uptime": 12345, "version": "1.0.0" }
  ```
- **/api/v1/status**
  ```json
  { "status": "ok", "projects": 3, "documents_indexed": 120, "last_ingest": "2025-06-24T12:34:56Z" }
  ```
- **/api/v1/projects**
  ```json
  { "projects": [ { "id": "my-dsl", "name": "My DSL Project", "documents": 42 } ] }
  ```
- **/api/v1/projects/{project_id}/sources**
  ```json
  { "sources": [ { "path": "src/grammar.dsl", "last_modified": "2025-06-24T12:00:00Z", "size": 1234 } ] }
  ```
- **/api/v1/logs**
  ```json
  { "logs": [ { "timestamp": "2025-06-24T12:34:56Z", "level": "INFO", "message": "Ingested file src/grammar.dsl" } ] }
  ```
- **/api/v1/metrics**
  ```json
  { "metrics": { "queries": 100, "ingest_events": 50, "errors": 2 } }
  ```
- **/api/v1/auth/token**
  ```json
  { "token": "jwt-or-api-token", "expires_in": 3600 }
  ```

All responses should include a top-level `status` or `error` field for clarity. Use ISO8601 for timestamps. Optional fields (like `error`) should be `null` if not present.

---

## Additional API Endpoints

The following endpoints are recommended for administration, health, and project/source management:

- `POST /api/v1/admin/reset` — Resets or clears the vector database/index (admin only).
- `POST /api/v1/admin/reindex` — Triggers a full re-ingestion and re-indexing for a project (admin only).
- `GET /api/v1/health` — Returns service health status.
- `GET /api/v1/status` — Returns current status and statistics.
- `GET /api/v1/projects` — Lists all known projects.
- `GET /api/v1/projects/{project_id}/sources` — Lists all source files/documents for a project.
- `POST /api/v1/ingest/full` — Triggers a full ingestion for a project.
- `DELETE /api/v1/ingest/source` — Removes a specific file/document from the index.
- `GET /api/v1/logs` — Returns recent logs (admin only).
- `GET /api/v1/metrics` — Returns service metrics.
- `POST /api/v1/auth/token` — Issues or refreshes an API token (if using token-based auth).

Admin endpoints should be protected and require authentication/authorization.

---

## Authentication

Authentication is disabled by default for the initial, sole-developer use case. The API and implementation are designed so that authentication (e.g., bearer token) can be enabled later with minimal changes. Admin endpoints should be protected if authentication is enabled in the future.

## Error Handling & Status Codes

All endpoints return appropriate HTTP status codes (e.g., 200 for success, 400 for bad request, 401 for unauthorized if auth is enabled, 404 for not found, 500 for server error). Error responses include a JSON object with a `status` of `error` and an `error` message.

Example error response:
```json
{ "status": "error", "error": "Description of the problem" }
```

## Versioning

All endpoints are versioned under `/api/v1/` to support future changes and backward compatibility.

## Extensibility Notes

- Authentication can be enabled by adding a bearer token check to the API and updating the client to send the token in the `Authorization` header.
- Pagination, filtering, and rate limiting can be added to list endpoints if data volume grows.
- CORS can be enabled if browser access is needed.
- The API is designed to be extensible for multi-user or production scenarios.

---

## Project and Tag Identifiers

All projects and tags are identified by lexicographically sortable, globally unique EUIDs (e.g., ULID). This enables efficient sorting, pagination, and time-based queries, and avoids ambiguity or collisions from human-friendly names. The API and UI map human-readable names to EUIDs as needed.

Example project object:
```json
{
  "id": "01HZY6QK7ZJ8X4Q2K7Q2K7Q2K7",
  "name": "my-dsl-project"
}
```

---

## Technology Stack

The following technologies, libraries, and tools are selected for the implementation of the file-watcher sidecar and RAG LLM Interface Service:

- **RAG Pipeline:** [LangChain](https://python.langchain.com/) for chunking, retrieval, and LLM context assembly.
- **API:** [FastAPI](https://fastapi.tiangolo.com/) for REST endpoints and OpenAPI docs.
- **File Watching:** [Watchdog](https://pythonhosted.org/watchdog/) for cross-platform file system event monitoring.
- **Vector Database:** SQLite with [sqlite-vss](https://github.com/asg017/sqlite-vss) or [sqlite-vector](https://github.com/keithito/sqlite-vector) extension, orchestrated by LangChain for local/solo use.
- **LLM Integration:** [Ollama](https://ollama.com/) for local LLM inference (default for privacy and offline use), with LangChain managing prompt assembly and context injection.
- **Authentication:** Python standard libraries, with optional [python-jose](https://github.com/mpdavis/python-jose) for JWT if/when bearer token auth is enabled.

These choices align with the ADRs and ensure the system is robust, extensible, and easy to maintain or migrate for future production scenarios.

---

## Development Practices & Documentation

- **Coding Style:**
  - All Python code follows [PEP8](https://peps.python.org/pep-0008/) style guidelines, with type hints and [PEP257](https://peps.python.org/pep-0257/) docstrings for all public modules, classes, and functions.
  - Use [black](https://github.com/psf/black) for automatic code formatting and [flake8](https://github.com/PyCQA/flake8) for linting.
  - Code reviews are required for all non-trivial changes.

- **Documentation:**
  - The project uses a literate programming style: code is documented inline with rich docstrings and explanatory comments.
  - [Sphinx](https://www.sphinx-doc.org/) is used to generate API documentation from docstrings and to build user/developer guides.
  - All modules and functions must have clear, example-driven docstrings. Where appropriate, use Sphinx's reStructuredText or Markdown support for formatting.
  - Documentation is versioned and published alongside releases.

- **Dependency Management:**
  - Use Poetry for all dependency and environment management. Run `poetry install` to set up the environment and dependencies.
  - The `pyproject.toml` file is the single source of truth for dependencies. Do not manually edit `requirements.txt`.
  - For alternative workflows (e.g., conda), use `environment.yml` to create a base environment, then use Poetry for Python dependencies.

- **Testing & CI:**
  - All new features and bugfixes require corresponding unit or integration tests (pytest).
  - Continuous integration runs linting, formatting, and tests on all pull requests.

- **Contribution Guidelines:**
  - A CONTRIBUTING.md file will provide detailed instructions for code style, documentation, testing, and the review process.

These practices ensure code quality, maintainability, and a consistent developer experience.
