ADR-0010: Vector Database
=========================

Status
------
Accepted

Context
-------
The system requires a local, lightweight, and reliable vector database to support retrieval-augmented generation (RAG) for code and document chunks. The database must support project-based isolation, recursive directory ingestion, and efficient similarity search for LLM context assembly. Scalability and migration to a distributed vector DB are future considerations, but SQLite is chosen for its simplicity and suitability for solo/local use.

Decision
--------
- Use SQLite as the vector store for all code/document chunk embeddings and metadata.
- Each chunk is stored with a unique ID in the form `file_path::chunkN`.
- The `project_id` is stored for each chunk, as provided by the API payload, enabling project-based retrieval and isolation.
- The file path is stored as metadata (in the `tag` column) for filtering, recursive ingestion, and source display.
- The database file path is configurable via the `RAGMS02_VECTOR_DB` environment variable, allowing persistent or in-memory operation.
- LangChain is used for chunking, embedding, and retrieval orchestration.

Consequences
------------
- Enables robust, recursive ingestion of directory structures and multi-project support.
- Retrieval is efficient and project-aware, supporting granular LLM context assembly.
- The design is extensible for future migration to distributed or cloud-native vector DBs.
- The approach is simple, reliable, and easy to operate for local/solo use cases.
