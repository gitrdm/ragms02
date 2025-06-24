from fastapi import APIRouter, Path
import os
from ragms02.vectorstore.langchain_sqlite import SQLiteLangChainVectorStore
from typing import List
import datetime

router = APIRouter()

@router.post("/admin/reset")
def admin_reset():
    """
    .. :no-index:

    Reset/clear the vector database/index (admin only).

    Returns:
        dict: Status and message.

    Example:
        >>> admin_reset()
        {'status': 'reset', 'message': 'Database/index has been cleared.'}
    """
    db_path = os.environ.get("RAGMS02_VECTOR_DB", ":memory:")
    store = SQLiteLangChainVectorStore(db_path)
    store.conn.execute("DELETE FROM vectors")
    store.conn.commit()
    store.close()
    return {"status": "reset", "message": "Database/index has been cleared."}

@router.post("/admin/reindex")
def admin_reindex():
    """
    .. :no-index:

    Trigger a full re-ingestion and re-indexing for a project (admin only).

    Returns:
        dict: Status and message.

    Example:
        >>> admin_reindex()
        {'status': 'reindexing', 'message': 'Reindexing started for project.'}
    """
    # Placeholder: In a real system, this would trigger a background job or workflow
    return {"status": "reindexing", "message": "Reindexing started for project."}

@router.get("/status")
def status():
    """
    .. :no-index:

    Returns current status and statistics.

    Returns:
        dict: Status, project count, document count, and last ingest time.

    Example:
        >>> status()
        {'status': 'ok', 'projects': 1, 'documents_indexed': 10, 'last_ingest': '...'}
    """
    db_path = os.environ.get("RAGMS02_VECTOR_DB", ":memory:")
    store = SQLiteLangChainVectorStore(db_path)
    cur = store.conn.execute("SELECT COUNT(DISTINCT project_id), COUNT(*) FROM vectors")
    projects, documents_indexed = cur.fetchone()
    cur = store.conn.execute("SELECT MAX(rowid) FROM vectors")
    last_ingest = datetime.datetime.utcnow().isoformat() + "Z"
    store.close()
    return {"status": "ok", "projects": projects, "documents_indexed": documents_indexed, "last_ingest": last_ingest}

@router.get("/projects")
def list_projects():
    """
    .. :no-index:

    Lists all known projects.

    Returns:
        dict: List of projects and document counts.

    Example:
        >>> list_projects()
        {'projects': [{'id': 'proj1', 'documents': 5}]}
    """
    db_path = os.environ.get("RAGMS02_VECTOR_DB", ":memory:")
    store = SQLiteLangChainVectorStore(db_path)
    cur = store.conn.execute("SELECT project_id, COUNT(*) FROM vectors GROUP BY project_id")
    projects = [{"id": row[0], "documents": row[1]} for row in cur]
    store.close()
    return {"projects": projects}

@router.get("/projects/{project_id}/sources")
def list_project_sources(project_id: str = Path(...)):
    """
    .. :no-index:

    Lists all source files/documents for a project.

    Args:
        project_id (str): Project identifier.

    Returns:
        dict: List of sources with path and snippet.

    Example:
        >>> list_project_sources("proj1")
        {'sources': [{'path': 'file1.txt', 'snippet': '...'}]}
    """
    db_path = os.environ.get("RAGMS02_VECTOR_DB", ":memory:")
    store = SQLiteLangChainVectorStore(db_path)
    cur = store.conn.execute("SELECT id, content FROM vectors WHERE project_id=?", (project_id,))
    sources = [{"path": row[0], "snippet": row[1][:100]} for row in cur]
    store.close()
    return {"sources": sources}

@router.get("/logs")
def get_logs():
    """
    .. :no-index:

    Returns recent logs (admin only). Placeholder implementation.

    Returns:
        dict: List of log entries.

    Example:
        >>> get_logs()
        {'logs': [{'timestamp': '...', 'level': 'INFO', 'message': 'Ingested file ...'}]}
    """
    # In a real system, fetch from a log store or file
    return {"logs": [{"timestamp": datetime.datetime.utcnow().isoformat() + "Z", "level": "INFO", "message": "Ingested file src/grammar.dsl"}]}

@router.get("/metrics")
def get_metrics():
    """
    .. :no-index:

    Returns service metrics. Placeholder implementation.

    Returns:
        dict: Metrics summary.

    Example:
        >>> get_metrics()
        {'metrics': {'queries': 100, 'ingest_events': 50, 'errors': 2}}
    """
    return {"metrics": {"queries": 100, "ingest_events": 50, "errors": 2}}
