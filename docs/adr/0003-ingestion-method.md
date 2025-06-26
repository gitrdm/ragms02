# ADR-0003: Document and Code Ingestion Method

## Status
Accepted

## Context
The RAG LLM Interface Service must ingest various document types, including code repositories, custom DSLs, and standard documentation formats (Markdown, PDF, plain text, HTML, etc.), to facilitate context-rich LLM responses. The underlying codebases and documents may change dynamically, requiring both initial full ingestions and ongoing incremental updates.

Supported file types include (but are not limited to):
- Source code: `.py`, `.js`, `.ts`, `.java`, `.go`, `.c`, `.cpp`, `.rb`, `.sh`, `.cs`, `.dsl`, etc.
- Documentation: `.md`, `.txt`, `.rst`, `.html`, `.pdf`
- Configs: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`

File patterns and types are configurable per project.

Potential ingestion methods include:
- API-based manual uploads/triggers
- Directory polling
- File system event watching
- Git repository hooks
- Manual admin/CLI triggers

For a dynamically evolving codebase, especially one using custom DSLs, timely ingestion of updates is critical for accurate LLM context.

## Decision

The system will support a **hybrid ingestion workflow** using LangChain for chunking, embedding, and retrieval orchestration:

### 1. Manual/API-Triggered Full Loads
- Users can manually trigger full ingestion of a codebase or document set via the REST API or CLI/admin interface.
- This is intended for onboarding new projects, major refactors, or periodic full re-indexing.
- **LangChain's text splitters** are used to chunk documents/code into LLM-optimized segments for embedding and storage.

### 2. Automated Incremental Updates via File-Watcher Sidecar
- A lightweight "sidecar" file-watcher process runs alongside the codebase (e.g., on the developer's machine or CI server).
- The watcher monitors specified directories and file patterns for changes (creation, modification, deletion).
- On detecting changes, the watcher notifies the RAG service by calling its ingestion API, submitting only the changed/affected files or metadata.
- The sidecar is decoupled from the RAG service, allowing flexibility in deployment (local, containerized, remote).
- **LangChain** is used to process changed files, chunking and embedding them for vector storage.

### 3. Extensibility for Other Triggers
- The architecture leaves room for future integration with git hooks, CI pipelines, or directory polling as needed.

## Payload and API Details
- The ingestion API expects a JSON payload as described in the API Design ADR and SDD, including project EUID, normalized file paths, event types, timestamps, and optionally file UUIDs, content hashes, file content, or storage references.
- See [ADR-0004 API Design](./0004-api-design.md) and the SDD for full payload schema and examples.
- **LangChain** orchestrates chunking and embedding for all ingested content.

## Error Handling and Retries
- The file-watcher sidecar implements retries with exponential backoff for failed API calls.
- Events are queued locally if the network or API is unavailable, and retried until successful.
- All errors and retries are logged for observability.

## Security Considerations
- Authentication is disabled by default for local/solo use, but the API and sidecar are designed to support bearer token authentication if enabled in the future.
- Sensitive data (e.g., API tokens) should be provided via environment variables and not stored in source control.

## Example Workflow
1. Developer saves a file (`src/main.py`).
2. File-watcher detects the change and batches the event.
3. After debounce, the watcher sends a payload to `/api/v1/ingest/notify`:
   ```json
   {
     "project_id": "01HZY6QK7ZJ8X4Q2K7Q2K7Q2K7",
     "events": [
       { "path": "src/main.py", "event_type": "modified", "timestamp": "2025-06-24T12:35:01Z" }
     ]
   }
   ```
4. The RAG service ingests the updated file and updates its vector index.
5. The watcher logs the successful ingestion.

## Ignore Patterns for Ingestion and File Watching

The ingestion system and file-watcher sidecar both support robust exclusion of files and directories using a shared `.ragignore` file. This file uses `.gitignore`-style syntax and can be customized per project. The ignore logic is implemented using the `pathspec` library and a shared utility, ensuring that both real-time and batch ingestion respect the same patterns.

- On startup, the watcher loads `.ragignore` and applies the patterns to all file system events.
- Bulk ingestion scripts also load `.ragignore` and skip ignored files/directories during recursive scans.
- Patterns can be customized to exclude any files, directories, or file types as needed.

See `ignore_utils.py`, `examples/watch_with_ragignore.py`, `examples/bulk_ingest.py`, and `examples/watch_exclude_examples_dir.py` for implementation details and usage examples.

---

## Consequences
- Ensures the RAG system is always up-to-date with the latest code and DSL changes.
- Manual full loads give explicit control for major events or recovery.
- Automated incremental updates minimize latency and compute by only re-ingesting changed files.
- The decoupled sidecar approach works across various environments and keeps the RAG service simple and agnostic to codebase specifics.
- Requires the sidecar watcher to be installed/configured per codebase/project.

## Extensibility Notes
- New ingestion triggers (e.g., git hooks, CI/CD) can be added by extending the sidecar or integrating with the API.
- Additional file types and patterns can be configured as project needs evolve.