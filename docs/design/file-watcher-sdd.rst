System Design Document: File-Watcher Sidecar and RAG LLM Interface Service
===========================================================================

Status
------
**Milestone Complete:**  
All ADRs have been finalized and incorporated. This SDD is up to date, implementation-ready, and reflects all architectural decisions regarding ingestion API, payload format, authentication, security, LLM routing, and deployment. No pending updates remain for this milestone.

Overview
--------
This document describes the architecture and implementation plan for the file-watcher sidecar and its integration with the RAG LLM Interface Service. The system uses **LangChain** as the core RAG pipeline for chunking, retrieval, and LLM context assembly. LangChain enables LLM-optimized chunking, efficient similarity search, and robust context construction for LLM queries. The system monitors file changes in code repositories and document directories, supports project/tag isolation using EUIDs, and notifies the RAG LLM Interface Service for both full and incremental ingestion. The design is robust for solo/local use but is extensible for future multi-user or production scenarios, supporting hybrid ingestion, flexible API/LLM routing, and secure, observable operations.

LLM Routing and Provider Selection
---------------------------------
- By default, all queries are answered using **Google Gemini** ("gemini-pro").
- Users can override the LLM provider/model per query by specifying the `model` (and optionally `provider`) field in the `/query` payload.
- Supported models/providers include Gemini ("gemini-pro"), Ollama (e.g., "llama2"), OpenAI (e.g., "gpt-3.5-turbo"), and are extensible.
- The default model/provider can be set via environment variable (e.g., `RAGMS02_DEFAULT_MODEL=gemini-pro`).
- The backend uses a dispatcher to route requests to the correct LLM provider based on the query payload.
- See the OpenAPI spec for example payloads and supported options.

Goals
-----
- Detect file changes (create, modify, delete, move/rename) in specified directories.
- Efficiently notify the ingestion API with only the changed/affected files.
- Support configuration for file patterns, directories, batching, and debounce intervals.
- Support project and tag isolation using EUIDs (ULID), enabling multi-project and multi-tag queries.
- Enable hybrid ingestion: full project loads and incremental updates via file-watcher.
- Provide robust, versioned RESTful API endpoints with per-query LLM routing and extensibility.
- Be extensible for future triggers (e.g., git hooks, CI/CD) and multi-user/production deployment.
- Handle operational concerns such as error handling, retries, observability, and secure configuration.

Out of Scope
------------
- Parsing/ingesting file content (handled by the RAG service).
- Full project scanning (except for initial load).
- Direct integration with git or other VCS (future work).

Architecture
------------

.. (continue with the rest of the SDD content as needed)
