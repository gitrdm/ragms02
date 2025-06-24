# Project Tagging and Multi-Tenancy

## Status
Accepted

## Context
The system may manage multiple projects and needs to keep their data isolated. Tagging allows for flexible grouping, filtering, and retrieval of documents, code, and vectors. Multi-tenancy is not required for solo/local use, but the design should support it for future scaling and advanced queries.

## Decision
- Each project is identified by a unique, sortable EUID (see ADR-0002).
- All ingested data (documents, vectors, metadata) is tagged with the project EUID.
- Additional tags (e.g., “docs”, “code”, “archived”) can be attached to files or vectors for flexible filtering and retrieval.
- The API supports specifying a list of project EUIDs and/or tags in a query, enabling context aggregation across multiple projects or tagged groups.
- The storage and retrieval logic ensures strict isolation between projects by default (no cross-project retrieval unless explicitly requested).

## Consequences
- Enables clean separation of data between projects.
- Flexible tagging supports advanced filtering, organization, and cross-project queries.
- Ready for future multi-user or multi-tenant scenarios.

## Alternatives Considered
- No tagging (harder to filter or group data).
- Flat namespace (risk of collisions, no isolation).

## References
- [ADR-0002 Project Identifiers](./0002-project-identifiers)
- System Design Document (SDD)
- API Design ADR
