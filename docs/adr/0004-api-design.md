# API Design

## Status
Accepted

## Context
The file-watcher sidecar and the RAG LLM Interface Service must communicate efficiently and reliably. The API design will define how file change notifications are sent, how ingestion is triggered, and how clients query for LLM-augmented results. The API should be easy to use, versioned, and support future extensibility. While the initial use case assumes the microservice and client are on the same machine, the API is designed to support future remote/server deployments as well.

## Decision
We will use a RESTful HTTP API for communication between the file-watcher and the RAG LLM Interface Service. REST is widely supported, easy to integrate with many languages, and well-suited for stateless, event-driven notifications. The API will use JSON payloads for compatibility and ease of debugging.

- **Endpoints:**
  - `POST /api/v1/ingest/notify` — Receives file change notifications from the file-watcher.
  - `POST /api/v1/query` — Accepts user queries and returns LLM-augmented responses.
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
- **Payloads:**
  - File change notifications will include project ID, normalized project-root-relative file paths, event types, timestamps, and optionally file UUIDs, content hashes, file content, or storage references. This extensible schema allows for robust identification and future remote/server support.
  - Query requests will include user query, project(s), and optional context parameters.
  - **LLM responses** will be structured as follows:
    - `response`: The LLM’s answer, possibly including DSL code or examples.
    - `sources`: Array of supporting sources, each with `path`, `snippet`, and optional `score`.
    - `citations`: (Optional) Inline mapping of answer segments to sources.
    - `confidence`: (Optional) LLM’s confidence in the answer.
    - `error`: (Optional) For error or fallback messages.

    Example:
    ```json
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
- **Versioning:**
  - All endpoints are versioned under `/api/v1/` to support future changes.

## Authentication

For the initial, sole-developer use case, authentication is disabled by default for simplicity. The API is designed so that authentication (e.g., bearer token) can be enabled later with minimal changes. Admin endpoints should be protected if authentication is enabled in the future.

## Error Handling & Status Codes

All endpoints return appropriate HTTP status codes (e.g., 200 for success, 400 for bad request, 401 for unauthorized if auth is enabled, 404 for not found, 500 for server error). Error responses include a JSON object with a `status` of `error` and an `error` message.

Example error response:
```json
{ "status": "error", "error": "Description of the problem" }
```

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

## Extensibility Notes

- Authentication can be enabled by adding a bearer token check to the API and updating the client to send the token in the `Authorization` header.
- Pagination, filtering, and rate limiting can be added to list endpoints if data volume grows.
- CORS can be enabled if browser access is needed.
- The API is designed to be extensible for multi-user or production scenarios.

## Consequences
- **Pros:**
  - Simple, language-agnostic integration
  - Easy to test and debug (curl, Postman, etc.)
  - Supports stateless, scalable deployment
  - Extensible for remote/server scenarios
- **Cons:**
  - Not as efficient as gRPC for high-throughput or streaming use cases
  - May require additional endpoints for advanced features in the future

## Alternatives Considered
- **gRPC:** More efficient for high-throughput, but adds complexity and less accessible for simple integrations.
- **WebSockets:** Useful for real-time updates, but not needed for current event-driven design.

## Implementation Notes
- The microservice should not assume direct file system access; it should rely on the event payload for file identity and, if needed, file content or storage reference.
- The watcher and API should support additional fields (e.g., file UUID, content hash, content, storage_url) for future extensibility.

## References
- [openapi.yaml](../openapi.yaml) — Canonical OpenAPI (Swagger) specification for all API endpoints, schemas, and error formats.
- [RESTful API Design](https://restfulapi.net/)
- [JSON API Spec](https://jsonapi.org/)

---
