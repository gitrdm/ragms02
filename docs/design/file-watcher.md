## Status

**Milestone Complete (Pending ADRs):**  
This TDD is considered complete for the current milestone.  
However, sections related to the ingestion API, payload format, and authentication are subject to change based on the outcomes of the following ADRs:
- [ADR-0003 Ingestion Method](./0003-ingestion-method.md)
- [ADR-9999 Decision Backlog](./9999-decision-backlog.md)

**Pending Updates:**  
- Final API endpoint and payload structure
- Authentication and security model
- Platform/deployment requirements

The TDD will be updated as these ADRs are finalized.

# Technical Design Document: File-Watcher Sidecar

## Overview

This document describes the design and implementation plan for the file-watcher sidecar, responsible for monitoring file changes in code repositories and document directories, and notifying the RAG LLM Interface Service for incremental ingestion.

---

## Goals

- Detect file changes (create, modify, delete, move/rename) in specified directories.
- Efficiently notify the ingestion API with only the changed/affected files.
- Support configuration for file patterns, directories, batching, and debounce intervals.
- Be extensible for future triggers (e.g., git hooks, CI/CD).
- Handle operational concerns such as error handling, retries, and observability.

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

- [ADR-0003 Ingestion Method](./0003-ingestion-method.md)
- [ADR-9999 Decision Backlog](./9999-decision-backlog.md)
- [watchdog Python project](https://github.com/gorakhargosh/watchdog)
- [RAG ingestion API docs] (TBD)

---

## Ingestion API Endpoints and Payloads

### Endpoint: Notify File Changes
- **Method:** POST
- **Path:** `/api/v1/ingest/notify`
- **Description:** Receives batched file change notifications from the file-watcher sidecar.

#### Request Payload (JSON)
```
{
  "project_id": "string",           // Project identifier
  "events": [
    {
      "path": "string",             // Relative or absolute file path
      "event_type": "created|modified|deleted|moved", // Type of change
      "timestamp": "ISO8601 string", // Event time (UTC)
      "old_path": "string (optional)" // For moved/renamed events
    },
    // ...more events
  ]
}
```
- **Required fields:** `project_id`, `events[].path`, `events[].event_type`, `events[].timestamp`
- **Optional fields:** `events[].old_path` (for moved/renamed)

#### Example Request
```
POST /api/v1/ingest/notify
Content-Type: application/json
Authorization: Bearer <token>

{
  "project_id": "docs-site",
  "events": [
    { "path": "docs/README.md", "event_type": "modified", "timestamp": "2025-06-24T12:34:56Z" },
    { "path": "src/main.py", "event_type": "created", "timestamp": "2025-06-24T12:35:01Z" }
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
- **Description:** Accepts user queries and returns LLM-augmented responses.

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
  "query": "How do I configure the file watcher?",
  "projects": ["docs-site"]
}
```

#### Response
- **200 OK**: `{ "response": "string", "sources": [ ... ] }`
- **4xx/5xx**: Error message

---

## File/Directory Exclusion and Ignore Patterns

The ingestion system and file-watcher sidecar both support robust exclusion of files and directories using a shared `.ragignore` file. This file uses `.gitignore`-style syntax and can be customized per project. The ignore logic is implemented using the `pathspec` library and a shared utility, ensuring that both real-time and batch ingestion respect the same patterns.

- On startup, the watcher loads `.ragignore` and applies the patterns to all file system events.
- Bulk ingestion scripts also load `.ragignore` and skip ignored files/directories during recursive scans.
- Patterns can be customized to exclude any files, directories, or file types as needed.

See `examples/ignore_utils.py` and `examples/watch_with_ragignore.py` for implementation details.

---