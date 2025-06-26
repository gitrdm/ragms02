# File Change Detection Technology

## Status
Accepted

## Context
The file-watcher sidecar must reliably detect file changes (create, modify, delete, move/rename) in specified directories. The solution should be cross-platform (Linux, macOS, Windows), efficient for large codebases, and robust against edge cases (e.g., rapid file changes, network filesystems). The technology choice will impact performance, portability, and operational complexity.

## Decision
We will use the Python Watchdog library for file change detection.

Watchdog is cross-platform, actively maintained, and widely used in the Python ecosystem. It provides a simple API, good documentation, and robust handling of file system events. This choice aligns with our intent to use Python for the sidecar and enables easy integration with other Python-based tools and ML workflows.

## Consequences
- **Pros:**
  - Cross-platform support (Linux, macOS, Windows)
  - Well-documented and actively maintained
  - Integrates easily with Python scripts and ML workflows
  - Handles rapid file changes and edge cases robustly
- **Cons:**
  - Requires Python runtime in deployment environments
  - Slightly higher memory usage than some native solutions
  - Not ideal if the stack shifts away from Python in the future

## Alternatives Considered
- **inotify (Linux):** Native, efficient, but Linux-only.
- **fswatch:** Cross-platform, CLI-based, but less flexible and requires extra scripting.
- **chokidar (Node.js):** Popular and robust, but best suited for Node.js stacks.
- **Polling:** Universal fallback, but less efficient and higher resource usage.

## File/Directory Exclusion and Ignore Patterns

The file-watcher sidecar and bulk ingestion scripts both support robust exclusion of files and directories using a shared `.ragignore` file. This file uses `.gitignore`-style syntax and can be customized per project. The ignore logic is implemented using the `pathspec` library and a shared utility, ensuring that both real-time and batch ingestion respect the same patterns.

- On startup, the watcher loads `.ragignore` and applies the patterns to all file system events.
- Bulk ingestion scripts also load `.ragignore` and skip ignored files/directories during recursive scans.
- Patterns can be customized to exclude any files, directories, or file types as needed.

See `examples/ignore_utils.py` and `examples/watch_with_ragignore.py` for implementation details.

## References
- [Watchdog Python](https://github.com/gorakhargosh/watchdog)
- [chokidar Node.js](https://github.com/paulmillr/chokidar)
- [fswatch](https://github.com/emcrisostomo/fswatch)
- [inotify man page](https://man7.org/linux/man-pages/man7/inotify.7.html)

---
