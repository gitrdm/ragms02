# Initial Load and Resync Strategy

## Status
Accepted

## Context
The system must handle both initial ingestion (first load of a project) and resyncs (full or partial re-ingestion). Incremental updates are handled by the file-watcher, but full loads are needed for onboarding, recovery, or major refactors. Ensuring the vector index matches the current state of the project is critical for reliable retrieval.

## Decision
- On project creation or onboarding, perform a full ingestion of all supported files in the configured directories.
- Allow users to trigger a full resync via the API, CLI, or admin interface at any time.
- Incremental updates are handled automatically by the file-watcher sidecar.
- During a full load or resync, all existing vectors for the project are replaced or updated to match the current state of the files.
- The system logs the start, progress, and completion of full loads and resyncs for observability and troubleshooting.

## Consequences
- Ensures the vector index is always consistent with the current project state.
- Users have explicit control over when to perform a full resync.
- Incremental updates minimize compute and latency for ongoing changes.
- Full loads may be time-consuming for large projects, but are infrequent.

## Alternatives Considered
- Only incremental updates (risk of drift or missed changes).
- Only full loads (inefficient for large projects or frequent changes).
- Scheduled periodic full loads (possible for future, but not required for solo/local use).

## References
- [ADR-0003 Ingestion Method](./0003-ingestion-method.md)
- System Design Document (SDD)
- API Design ADR
