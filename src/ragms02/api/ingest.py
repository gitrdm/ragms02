from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ragms02.vectorstore.sqlite import VectorStore
from ragms02.vectorstore.embedding import embed_text
from ragms02.vectorstore.langchain_sqlite import SQLiteLangChainVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import base64
import os

router = APIRouter()

class FileEvent(BaseModel):
    """
    .. :no-index:

    Represents a file change event for ingestion.

    Attributes:
        path (str): Project-root-relative file path.
        event_type (str): Type of change (created, modified, deleted, moved).
        timestamp (datetime): Event time (UTC).
        uuid (Optional[str]): Optional stable file UUID.
        hash (Optional[str]): Optional content hash.
        content (Optional[str]): Optional file content (base64 or text).
        storage_url (Optional[str]): Optional reference to file in shared storage.
        old_path (Optional[str]): For moved/renamed events.

    Example:
        >>> FileEvent(path="docs/file.txt", event_type="created", timestamp=datetime.utcnow())
    """
    path: str
    event_type: str
    timestamp: datetime
    uuid: Optional[str] = None
    hash: Optional[str] = None
    content: Optional[str] = None
    storage_url: Optional[str] = None
    old_path: Optional[str] = None

class IngestNotifyRequest(BaseModel):
    """
    .. :no-index:

    Request payload for /ingest/notify endpoint.

    Attributes:
        project_id (str): Project identifier.
        events (List[FileEvent]): List of file events (see :class:`FileEvent`).

    Example:
        >>> IngestNotifyRequest(project_id="proj1", events=[FileEvent(...)])
    """
    project_id: str
    events: List[FileEvent]

CHUNK_SIZE = 300  # characters per chunk
CHUNK_OVERLAP = 50

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """
    .. :no-index:

    Split text into LLM-optimized chunks using LangChain's text splitter.

    Args:
        text (str): The input text to split.
        size (int): Chunk size in characters.
        overlap (int): Overlap between chunks.

    Returns:
        List[str]: List of text chunks.

    Example:
        >>> chunk_text("This is a long document...", size=100, overlap=10)
        ['This is a long doc...', ...]
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    return splitter.split_text(text)

@router.post("/ingest/notify")
def ingest_notify(payload: IngestNotifyRequest):
    """
    .. :no-index:

    Ingest file change events: chunk, embed, and update vector store using LangChain.

    Args:
        payload (IngestNotifyRequest): Ingestion request payload (see :class:`IngestNotifyRequest`).

    Returns:
        dict: Status and number of processed chunks/events.

    Example:
        >>> req = IngestNotifyRequest(project_id="proj1", events=[FileEvent(...)])
        >>> ingest_notify(req)
        {'status': 'success', 'processed': 3}
    """
    db_path = os.environ.get("RAGMS02_VECTOR_DB", ":memory:")
    store = SQLiteLangChainVectorStore(db_path)
    processed = 0
    for event in payload.events:
        if event.event_type in ("created", "modified"):
            content = event.content
            if content is None and os.path.exists(event.path):
                with open(event.path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            if content is not None:
                chunks = chunk_text(content)
                documents = []
                embeddings = []
                for idx, chunk in enumerate(chunks):
                    doc_id = f"{event.path}::chunk{idx}"
                    print(f"[DEBUG] Storing doc_id: {doc_id}, project_id: {payload.project_id}, chunk: {repr(chunk)}")
                    documents.append(Document(page_content=chunk, metadata={"id": doc_id, "file_path": event.path}))
                    embeddings.append(embed_text(chunk))
                # Pass project_id as a keyword argument
                store.add_documents(documents, embeddings, project_id=payload.project_id)
                processed += len(documents)
        elif event.event_type == "deleted":
            prefix = event.uuid or event.path
            store.conn.execute("DELETE FROM vectors WHERE id LIKE ?", (f"{prefix}::chunk%",))
            store.conn.commit()
            processed += 1
    store.close()
    return {"status": "success", "processed": processed}
