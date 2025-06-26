workspace {

    model {
        user = person "Local App/User" "A local application or user that interacts with the LLM interface service"

        fileWatcher = softwareSystem "File-Watcher Sidecar" "Monitors file changes in code and document directories, batching and sending events to the RAG LLM Interface Service. Uses Watchdog for cross-platform file monitoring."

        ragService = softwareSystem "RAG LLM Interface Service" "Provides enhanced, context-aware LLM responses to local applications. Handles ingestion, retrieval, vectorization, and LLM routing."
        
        langchain = container "LangChain RAG Pipeline" "Orchestrates chunking, retrieval, vector DB, and LLM routing for all RAG operations. Powers ingestion, retrieval, and context assembly." "Python LangChain"
        api = container "API Handler" "REST API for querying, ingestion, and orchestration. Implements versioned endpoints, error handling, and authentication (optional)." "Python FastAPI"
        ingestion = container "Ingestion Service" "Handles document and code ingestion, initial full loads, incremental updates, chunking, and vectorization. Uses LangChain for chunking and embedding." "Python, LangChain, PyYAML, Requests, ULID-py"
        vectordb = container "Vector Database" "Stores vector embeddings, tagged by project and tag EUIDs. Uses SQLite with vector extension for local/solo use, orchestrated by LangChain." "SQLite + sqlite-vss/sqlite-vector"
        retrieval = container "Retrieval & Indexing" "Performs similarity search and gathers context for LLM queries, filtered by project/tag. Uses LangChain for retrieval and context assembly."
        llmRouter = container "LLM Router" "Routes requests to local or cloud LLMs; supports per-query and global routing preferences. Managed by LangChain."
        llmLocal = container "Local LLM" "Ollama or other locally hosted LLMs"
        llmCloud = container "Cloud LLM" "Google Gemini or other cloud-hosted LLM services"

        user -> fileWatcher "Triggers file changes (save, edit, etc.)"
        fileWatcher -> api "Sends batched file change notifications (project/tag EUIDs, events)"
        user -> api "Submits queries and ingestion requests"
        api -> langchain "Sends all ingestion and query requests to LangChain RAG pipeline"
        langchain -> ingestion "Handles chunking, embedding, and ingestion orchestration"
        langchain -> vectordb "Stores and retrieves vector embeddings by project/tag EUIDs"
        langchain -> retrieval "Performs similarity search and context assembly"
        langchain -> llmRouter "Routes context and queries to LLMs"
        llmRouter -> llmLocal "Routes to local LLM (default: Ollama)"
        llmRouter -> llmCloud "Routes to cloud LLM (default: Gemini)"
        llmLocal -> llmRouter "Returns generated response"
        llmCloud -> llmRouter "Returns generated response"
        llmRouter -> langchain "Returns LLM response"
        langchain -> api "Returns answer and context"
        api -> user "Returns answer and context"
    }

    views {
        container ragService {
            include *
            autolayout lr
            title "RAG LLM Interface Service - Container Diagram"
            description "Main containers and data flows for the RAG LLM Interface Service and File-Watcher Sidecar, now with LangChain orchestrating chunking, retrieval, vector DB, and LLM routing."
        }
    }
}

## Ignore Patterns for Ingestion and File Watching

The ingestion system and file-watcher sidecar both support robust exclusion of files and directories using a shared `.ragignore` file. This file uses `.gitignore`-style syntax and can be customized per project. The ignore logic is implemented using the `pathspec` library and a shared utility, ensuring that both real-time and batch ingestion respect the same patterns.

- On startup, the watcher loads `.ragignore` and applies the patterns to all file system events.
- Bulk ingestion scripts also load `.ragignore` and skip ignored files/directories during recursive scans.
- Patterns can be customized to exclude any files, directories, or file types as needed.

See `examples/ignore_utils.py` and `examples/watch_with_ragignore.py` for implementation details.

---