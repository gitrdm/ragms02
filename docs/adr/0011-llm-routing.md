# LLM Routing and Model Selection

## Status
Accepted

## Context
The system may use different LLMs (local or cloud) for query augmentation. For solo/local use, a local LLM (e.g., Ollama, LM Studio, or similar) is preferred for privacy, cost, and offline capability. However, there may be cases where a cloud LLM (e.g., OpenAI, Gemini) is desired for more advanced capabilities or coverage. The system should allow easy switching between local and cloud LLMs, both globally and per query.

## Decision
- Default to a local LLM for all queries to maximize privacy and minimize cost.
- Allow configuration (via environment variable or config file) to select the default LLM backend (local or cloud) and model name/version.
- Support a per-query flag in the API request to override the default and explicitly route a query to either the local or cloud LLM.
- The API and client are designed to support future routing logic (e.g., fallback to cloud if local fails, or route by project/query type).

## Consequences
- Maximizes privacy and cost control for solo/local use.
- Provides flexibility to use cloud LLMs when needed, either globally or per query.
- Enables future multi-model or hybrid routing scenarios.
- Slightly more complexity in the API and client to support per-query routing.

## Alternatives Considered
- Always use cloud LLM (higher cost, requires internet, less privacy).
- Hard-code a single model (less flexible, not future-proof).
- Only allow global config, not per-query override (less flexible for advanced use cases).

## References
- System Design Document (SDD)
- [ADR-0004 API Design](./0004-api-design.md)
