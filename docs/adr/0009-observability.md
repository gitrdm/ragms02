# Observability and Logging

## Status
Accepted

## Context
The system should provide enough logging and metrics for debugging, monitoring, and troubleshooting, even for solo/local use. It should be easy to extend for more advanced observability in the future as the system scales or is deployed in production.

## Decision
- Log key events (startup, shutdown, file events, API calls, errors, retries) to stdout and to a rotating log file.
- Use a structured log format (e.g., JSON or key-value) for easy parsing and future integration with log aggregation tools.
- Expose basic metrics (e.g., number of changes detected, notifications sent, retries, queue depth) via a `/metrics` API endpoint (JSON format).
- Provide a `/health` endpoint for liveness checks.
- For solo/local use, logs and metrics are sufficient; distributed tracing is not required but can be added later if needed.

## Consequences
- Enables easy debugging and monitoring for solo/local use.
- Ready for extension to more advanced observability (e.g., Prometheus, OpenTelemetry) if needed in the future.
- Minimal overhead for local development and testing.

## Alternatives Considered
- No logging/metrics (not recommended).
- Full tracing/telemetry (overkill for solo/local, but possible for future scaling or production).

## References
- System Design Document (SDD)
- [ADR-0004 API Design](./0004-api-design.md)
