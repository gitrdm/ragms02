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

The system will support a **hybrid ingestion workflow** using LangChain for chunking, embedding, and retrieval orchestration:

1. Manual/API-Triggered Full Loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Users can manually trigger full ingestion of a codebase or document set via the REST API or CLI/admin interface.
- This is intended for onboarding new projects, major refactors, or periodic full re-indexing.
- **LangChain's text splitters** are used to chunk documents/code into LLM-optimized segments for embedding and storage.

2. Automated Incremental Updates via File-Watcher Sidecar
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- A lightweight "sidecar" file-watcher process runs alongside the codebase (e.g., on the developer's machine or CI server).
- The watcher monitors specified directories and file patterns for changes (creation, modification, deletion).
- On detecting changes, the watcher notifies the RAG service by calling its ingestion API, submitting only the changed/affected files or metadata.
- The sidecar is decoupled from the RAG service, allowing flexibility in deployment (local, containerized, remote).
- **LangChain** is used to process changed files, chunking and embedding them for vector storage.
