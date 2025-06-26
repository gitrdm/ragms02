ADR-0003: Document and Code Ingestion Method
============================================

Status
------
Accepted

Context
-------
The RAG LLM Interface Service must ingest various document types, including code repositories, custom DSLs, and standard documentation formats (Markdown, PDF, plain text, HTML, etc.), to facilitate context-rich LLM responses. The underlying codebases and documents may change dynamically, requiring both initial full ingestions and ongoing incremental updates.

Supported file types include (but are not limited to):

- Source code: ``.py``, ``.js``, ``.ts``, ``.java``, ``.go``, ``.c``, ``.cpp``, ``.rb``, ``.sh``, ``.cs``, ``.dsl``, etc.
- Documentation: ``.md``, ``.txt``, ``.rst``, ``.html``, ``.pdf``
- Configs: ``.json``, ``.yaml``, ``.yml``, ``.toml``, ``.ini``

File patterns and types are configurable per project.

Potential ingestion methods include:

- API-based manual uploads/triggers
- Directory polling
- File system event watching
- Git repository hooks
- Manual admin/CLI triggers

For a dynamically evolving codebase, especially one using custom DSLs, timely ingestion of updates is critical for accurate LLM context.

Decision
--------

The system supports a **hybrid ingestion workflow** using LangChain for chunking, embedding, and retrieval orchestration:

1. Manual/API-Triggered Full Loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Users can manually trigger full ingestion of a codebase or document set via the REST API or CLI/admin interface.
- This is intended for onboarding new projects, major refactors, or periodic full re-indexing.
- **LangChain's text splitters** are used to chunk documents/code into LLM-optimized segments for embedding and storage.
- Each chunk is stored with a unique ID (`file_path::chunkN`), the project ID (from the API payload), and the file path as metadata, supporting recursive directory ingestion and project-based retrieval.

2. Incremental Ingestion via File-Watcher
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- The file-watcher sidecar monitors directories for file changes (create, modify, delete, move/rename).
- Only changed/affected files are re-chunked and re-ingested, minimizing unnecessary work.
- Project and tag isolation is maintained for all ingested chunks.

3. Retrieval
^^^^^^^^^^^^
- Retrieval is project-based: queries specify one or more project IDs, and only chunks for those projects are considered.
- The vector store returns the most relevant chunks (by embedding similarity) for LLM context assembly.

Consequences
------------
- Enables robust, recursive ingestion of code/document directories.
- Supports multi-project, multi-tag, and incremental workflows.
- Retrieval is efficient and context-rich, supporting granular LLM responses.
