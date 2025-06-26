ADR-0006: File Change Detection
===============================

Status
------
Accepted

Context
-------
(Describe the context for file change detection, e.g., need for incremental ingestion, file-watcher, etc.)

Decision
--------
(Describe the approach for detecting file changes, e.g., using watchdog, polling, etc.)

Consequences
------------
(Describe the impact of this decision, e.g., performance, reliability, etc.)

File/Directory Exclusion and Ignore Patterns
---------------------------------------------

The file-watcher sidecar and bulk ingestion scripts both support robust exclusion of files and directories using a shared `.ragignore` file. This file uses `.gitignore`-style syntax and can be customized per project. The ignore logic is implemented using the `pathspec` library and a shared utility, ensuring that both real-time and batch ingestion respect the same patterns.

- On startup, the watcher loads `.ragignore` and applies the patterns to all file system events.
- Bulk ingestion scripts also load `.ragignore` and skip ignored files/directories during recursive scans.
- Patterns can be customized to exclude any files, directories, or file types as needed.

See `examples/ignore_utils.py` and `examples/watch_with_ragignore.py` for implementation details.
