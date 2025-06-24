# Vector Database Selection

## Status
Accepted

## Context
The system needs to store and search vector embeddings for documents and code. For solo/local use, simplicity, zero external dependencies, and portability are important. The solution should also allow for easy migration to a more scalable vector database if needed in the future.

## Decision
- Use SQLite with a vector extension (e.g., sqlite-vss, sqlite-vector) for local development and solo use.
- SQLite is lightweight, requires no server, and is easy to set up, back up, and move between environments.
- The codebase will abstract vector storage so it can be swapped for a scalable solution (e.g., Qdrant, Pinecone, Postgres+pgvector) later if needed.

## Consequences
- Fast, simple, and portable for local use.
- No external services or network dependencies required.
- May not scale for very large datasets or high-concurrency workloads.
- Easy migration path to a production-grade vector DB if requirements grow.

## Alternatives Considered
- **Qdrant:** Production-ready, scalable, but requires running a service.
- **Pinecone:** Managed cloud, not local/offline, paid for production use.
- **FAISS:** Fast, but not a database; requires custom persistence and metadata management.
- **DuckDB:** Great for analytics, but vector search support is limited and less mature.
- **Postgres+pgvector:** Good for hybrid search, but heavier than SQLite for solo/local use.

## References
- System Design Document (SDD)
- [sqlite-vss](https://github.com/asg017/sqlite-vss)
- [sqlite-vector](https://github.com/keithito/sqlite-vector)
