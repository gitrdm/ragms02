# Error Handling and Retry Policy

## Status
Accepted

## Context
The system must handle transient errors (e.g., network issues, temporary API failures) and ensure reliability for ingestion and query operations. For a solo/local-first setup, error handling should be robust but not overly complex. Reliability is especially important for ingestion events to prevent data loss.

## Decision
- Use retries with exponential backoff for transient errors (e.g., failed API calls to the ingestion service).
- Queue failed events locally (e.g., on disk) and retry until successful or a maximum retry count is reached.
- Log all errors and retries for observability and troubleshooting.
- Return clear, structured error responses in the API (with `status` and `error` message fields).
- For unrecoverable errors (e.g., invalid payload, persistent failures), surface a clear message to the user and require manual intervention.

## Consequences
- Improves reliability and user experience.
- Prevents data loss due to temporary failures.
- Adds some complexity to the client/sidecar for queueing and retry logic.
- May require disk space for local event queueing.

## Alternatives Considered
- No retries (risk of data loss and poor reliability).
- Immediate failure escalation (less robust for transient issues).
- Use of external queueing systems (overkill for solo/local use, but possible for future scaling).

## References
- [ADR-0004 API Design](./0004-api-design.md)
- System Design Document (SDD)
