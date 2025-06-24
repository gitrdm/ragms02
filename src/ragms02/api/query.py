from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from ragms02.llm.dispatcher import dispatch_llm
from ragms02.vectorstore.sqlite import VectorStore
from ragms02.vectorstore.embedding import embed_text
from ragms02.vectorstore.langchain_sqlite import SQLiteLangChainVectorStore
from langchain.schema import Document
import os

router = APIRouter()

class QueryRequest(BaseModel):
    """
    .. :no-index:

    Request payload for /query endpoint.

    Attributes:
        query (str): User's question or prompt.
        projects (List[str]): List of project IDs to search.
        context (Optional[Dict[str, Any]]): Additional context or parameters.
        model (Optional[str]): LLM model to use.

    Example:
        >>> QueryRequest(query="What is RAG?", projects=["proj1"])
    """
    query: str
    projects: List[str]
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = "llama2"

class QueryResponse(BaseModel):
    """
    .. :no-index:

    Response model for /query endpoint.

    Attributes:
        response (str): LLM answer.
        sources (Optional[List[Dict[str, Any]]]): Supporting sources.
        citations (Optional[List[Dict[str, Any]]]): Inline mapping of answer segments to sources.
        confidence (Optional[float]): LLM's confidence in the answer.
        error (Optional[str]): Error or fallback message.

    Example:
        >>> QueryResponse(response="RAG stands for...", sources=[{"id": "doc1"}])
    """
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

@router.post("/query", response_model=QueryResponse)
def query_llm(payload: QueryRequest):
    """
    .. :no-index:

    Retrieve similar docs using LangChain vector store and assemble context for LLM.

    Args:
        payload (QueryRequest): Query request payload (see :class:`QueryRequest`).

    Returns:
        QueryResponse: LLM response and supporting sources (see :class:`QueryResponse`).

    Example:
        >>> req = QueryRequest(query="What is RAG?", projects=["proj1"])
        >>> query_llm(req)
        QueryResponse(response="RAG stands for...", sources=[...])
    """
    db_path = os.environ.get("RAGMS02_VECTOR_DB", ":memory:")
    store = SQLiteLangChainVectorStore(db_path)
    project_id = payload.projects[0] if payload.projects else None
    sources = []
    context_chunks = []
    if project_id:
        query_emb = embed_text(payload.query)
        docs = store.similarity_search(
            query="",  # not used, expects embedding in filter
            k=5,
            filter={"embedding": query_emb, "project_id": project_id}
        )
        print("[DEBUG] Retrieved docs:")
        for doc in docs:
            print(f"[DEBUG] id: {doc.metadata.get('id')}, score: {doc.metadata.get('score')}, snippet: {doc.page_content}")
        for doc in docs:
            sources.append({"id": doc.metadata.get("id"), "score": doc.metadata.get("score"), "snippet": doc.page_content})
            context_chunks.append(doc.page_content)
    store.close()
    context = "\n".join(context_chunks)
    try:
        llm_response = dispatch_llm(
            payload.query + "\nContext:\n" + context,
            context=context_chunks,
            model=payload.model
        )
        return QueryResponse(response=llm_response, sources=sources)
    except Exception as e:
        return QueryResponse(response="", error=str(e))
