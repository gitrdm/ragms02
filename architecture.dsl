workspace {

    model {
        user = person "Local App/User" "A local application or user that interacts with the LLM interface service"

        fileWatcher = softwareSystem "File-Watcher Sidecar" "Monitors file changes in code and document directories, batching and sending events to the RAG LLM Interface Service. Uses Watchdog for cross-platform file monitoring."

        ragService = softwareSystem "RAG LLM Interface Service" "Provides enhanced, context-aware LLM responses to local applications. Handles ingestion, retrieval, vectorization, and LLM routing."
        
        api = container "API Handler" "REST API for querying, ingestion, and orchestration. Implements versioned endpoints, error handling, and authentication (optional)." "Python FastAPI"
        ingestion = container "Ingestion Service" "Handles document and code ingestion, initial full loads, incremental updates, chunking, and vectorization. Supports hybrid ingestion and project/tag isolation." "Python, PyYAML, Requests, ULID-py"
        vectordb = container "Vector Database" "Stores vector embeddings, tagged by project and tag EUIDs. Uses SQLite with vector extension for local/solo use." "SQLite + sqlite-vss/sqlite-vector"
        retrieval = container "Retrieval & Indexing" "Performs similarity search and gathers context for LLM queries, filtered by project/tag."
        llmRouter = container "LLM Router" "Routes requests to local or cloud LLMs; supports per-query and global routing preferences."
        llmLocal = container "Local LLM" "Ollama or other locally hosted LLMs"
        llmCloud = container "Cloud LLM" "Google Gemini or other cloud-hosted LLM services"

        user -> fileWatcher "Triggers file changes (save, edit, etc.)"
        fileWatcher -> api "Sends batched file change notifications (project/tag EUIDs, events)"
        user -> api "Submits queries and ingestion requests"
        api -> ingestion "Sends ingestion requests (documents, code, full or incremental)"
        ingestion -> vectordb "Stores vector embeddings by project/tag EUIDs"
        api -> retrieval "Sends query requests (with project/tag filters)"
        retrieval -> vectordb "Performs similarity search, filtered by project/tag"
        retrieval -> llmRouter "Sends context and query for generation"
        llmRouter -> llmLocal "Routes to local LLM (default: Ollama)"
        llmRouter -> llmCloud "Routes to cloud LLM (default: Gemini)"
        llmLocal -> llmRouter "Returns generated response"
        llmCloud -> llmRouter "Returns generated response"
        llmRouter -> api "Returns LLM response"
        api -> user "Returns answer and context"
    }

    views {
        container ragService {
            include *
            autolayout lr
            title "RAG LLM Interface Service - Container Diagram"
            description "Main containers and data flows for the RAG LLM Interface Service and File-Watcher Sidecar, including project/tag isolation, hybrid ingestion, error handling, observability, and extensibility."
        }
    }
}