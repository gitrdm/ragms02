# ADR-9999: Architecture Decision Backlog

## Context
Some technical design questions require further research or are deferred until implementation.

## Open Questions

- **File Change Detection:**  
  Should the file-watcher sidecar use file hashes, modification timestamps, filenames, or a combination to detect and identify changed files for ingestion? What are the tradeoffs for correctness, performance, and reliability?
  _Status: Addressed in File Change Detection ADR and SDD. The system uses modification timestamps by default, with optional file hashes for increased reliability. Tradeoffs are documented in the relevant ADRs._

- [Add other questions as they arise]