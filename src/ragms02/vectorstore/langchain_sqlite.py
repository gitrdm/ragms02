from langchain.vectorstores.base import VectorStore as LCVectorStore
from langchain.schema import Document
from typing import List, Optional, Any
import numpy as np
import sqlite3

class SQLiteLangChainVectorStore(LCVectorStore):
    """
    LangChain-compatible vector store using SQLite for local/solo use.

    Stores chunk embeddings, content, and metadata for RAG retrieval.

    Example:
        >>> store = SQLiteLangChainVectorStore(db_path=":memory:")
        >>> store.add_documents([Document(page_content="text", metadata={"id": "doc1"})], metadatas=[{"id": "doc1"}], ids=["doc1"])
        >>> docs = store.similarity_search("query text", k=5, filter={"project_id": "proj1"})
    """

    def __init__(self, db_path=":memory:"):
        """
        Initialize the SQLiteLangChainVectorStore.

        Args:
            db_path (str): Path to the SQLite database file. Defaults to in-memory database.

        Example:
            >>> store = SQLiteLangChainVectorStore(db_path=":memory:")
        """
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """
        Initialize the database schema.
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                tag TEXT,
                embedding BLOB,
                content TEXT
            )
        """)
        self.conn.commit()

    def add_documents(self, documents: List[Document], metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None, project_id: Optional[str] = None, **kwargs) -> List[str]:
        """
        Add documents and their embeddings to the SQLite vector store.

        Args:
            documents (List[Document]): List of LangChain Document objects.
            metadatas (Optional[List[dict]]): List of embedding vectors (should match documents).
            ids (Optional[List[str]]): List of document IDs.
            project_id (Optional[str]): Project identifier for all documents.
            **kwargs: Additional arguments.

        Returns:
            List[str]: List of document IDs added.
        """
        if metadatas is None:
            raise ValueError("Embeddings (metadatas) must be provided.")
        if len(documents) != len(metadatas):
            raise ValueError("Number of documents and embeddings must match.")
        doc_ids = []
        for i, (doc, emb) in enumerate(zip(documents, metadatas)):
            doc_id = doc.metadata.get("id", f"doc_{i}")
            file_path = doc.metadata.get("file_path", "")
            # Use provided project_id, not doc_id prefix
            db_project_id = project_id or "default"
            emb_bytes = np.array(emb, dtype=np.float32).tobytes()
            self.conn.execute(
                """
                INSERT OR REPLACE INTO vectors (id, project_id, tag, embedding, content)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doc_id, db_project_id, file_path, emb_bytes, doc.page_content)
            )
            doc_ids.append(doc_id)
        self.conn.commit()
        return doc_ids

    def similarity_search(self, query: str, k: int = 5, filter: Optional[dict] = None, **kwargs) -> List[Document]:
        """
        Return top-k most similar documents for a given project. (Signature matches LangChain base class.)

        Args:
            query (str): Query text (not used, expects embedding in filter).
            k (int): Number of results to return.
            filter (dict, optional): Filter dict, expects 'project_id' and 'embedding'.
            **kwargs: Additional arguments.

        Returns:
            List[Document]: Top-k similar documents.
        """
        # For compatibility, expects 'embedding' and 'project_id' in filter
        if not filter or "embedding" not in filter or "project_id" not in filter:
            return []
        embedding = filter["embedding"]
        project_id = filter["project_id"]
        cur = self.conn.execute("SELECT id, embedding, content FROM vectors WHERE project_id=?", (project_id,))
        q = np.array(embedding, dtype=np.float32)
        scored = []
        for row in cur:
            vec_id, emb_bytes, content = row
            v = np.frombuffer(emb_bytes, dtype=np.float32)
            sim = float(np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v) + 1e-8))
            print(f"[DEBUG] Similarity for doc_id: {vec_id} = {sim:.4f}")
            scored.append((vec_id, sim, content))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [Document(page_content=content, metadata={"id": vec_id, "score": score}) for vec_id, score, content in scored[:k]]

    def close(self):
        """
        Close the SQLite connection.

        Example:
            >>> store.close()
        """
        self.conn.close()

    @classmethod
    def from_texts(cls, texts: List[str], embedding: Any, metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None, **kwargs) -> 'SQLiteLangChainVectorStore':
        """
        Not implemented. Use add_documents directly for this store.
        """
        raise NotImplementedError("Use add_documents directly for this store.")

    def as_retriever(self, **kwargs) -> Any:
        """
        Minimal stub for LangChain compatibility.
        """
        return self
