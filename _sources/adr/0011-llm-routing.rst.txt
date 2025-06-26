ADR-0011: LLM Routing
=====================

Status
------
Accepted

Context
-------
The system must support multiple LLM providers and models, with a default (Google Gemini) but the ability to override per query. This enables flexibility for local, cloud, and future LLMs, and supports user and admin control over LLM selection.

Decision
--------
- The backend implements a dispatcher that routes LLM queries to the correct provider/model.
- By default, queries are answered using Gemini ("gemini-pro").
- Users can override the model/provider per query by specifying the `model` (and optionally `provider`) field in the `/query` payload.
- Supported providers/models include Gemini, Ollama, OpenAI, and are extensible.
- The dispatcher is config-driven and can be extended to support new providers.

Consequences
------------
- The system is flexible and future-proof, supporting new LLMs as they become available.
- Users and admins can control LLM selection per query or via configuration.
- Documentation and OpenAPI spec must clearly describe supported models/providers and override options.
