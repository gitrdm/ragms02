ADR-0004: API Design
=====================

Status
------
Accepted

Context
-------
The API must support robust, versioned RESTful endpoints for ingestion, querying, and admin operations. LLM routing is a core requirement: the system must default to Google Gemini for LLM queries, but allow per-request override to other providers/models (e.g., Ollama, OpenAI) for extensibility and user control.

Decision
--------
- The `/query` endpoint accepts a `model` (and optional `provider`) field to select the LLM provider/model for each request.
- If not specified, the backend defaults to Gemini ("gemini-pro").
- The backend uses a dispatcher to route queries to the correct LLM provider.
- Supported models/providers are documented in the OpenAPI spec and can be extended.
- Example payloads and usage are included in the OpenAPI spec.

Consequences
------------
- The API is flexible and future-proof, supporting new LLM providers/models as needed.
- Users can control LLM selection per query, but the system is safe and predictable by default (Gemini).
- Documentation and OpenAPI spec must be kept up to date with supported models/providers and example payloads.
