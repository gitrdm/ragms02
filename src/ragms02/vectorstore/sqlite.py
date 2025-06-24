import sqlite3
import numpy as np
from typing import List, Optional, Tuple

class VectorStore:
    """
    Simple SQLite-based vector store for storing and retrieving embeddings.

    Example:
        >>> store = VectorStore()
        >>> store.add_vector("vec1", "proj1", "created", b"...")
        >>> emb = store.get_vector("vec1")
        >>> results = store.similarity_search([0.1, 0.2, ...], "proj1", top_k=3)
    """
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize the VectorStore.

        Args:
            db_path (str): Path to the SQLite database file. Defaults to in-memory database.
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
                embedding BLOB
            )
        """)
        self.conn.commit()

    def add_vector(self, id: str, project_id: str, tag: str, embedding: bytes):
        """
        Add or update a vector in the store.

        Args:
            id (str): Vector ID.
            project_id (str): Project identifier.
            tag (str): Tag or event type.
            embedding (bytes): Serialized embedding vector.

        Example:
            >>> store.add_vector("vec1", "proj1", "created", b"...")
        """
        self.conn.execute(
            "INSERT OR REPLACE INTO vectors (id, project_id, tag, embedding) VALUES (?, ?, ?, ?)",
            (id, project_id, tag, embedding)
        )
        self.conn.commit()

    def get_vector(self, id: str) -> Optional[bytes]:
        """
        Retrieve a vector by its ID.

        Args:
            id (str): Vector ID.

        Returns:
            Optional[bytes]: Serialized embedding vector, or None if not found.

        Example:
            >>> emb = store.get_vector("vec1")
        """
        cur = self.conn.execute("SELECT embedding FROM vectors WHERE id=?", (id,))
        row = cur.fetchone()
        return row[0] if row else None

    def similarity_search(self, query_emb: List[float], project_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Return top_k (id, score) pairs most similar to query_emb for a given project.

        Cosine similarity is used for measuring similarity between vectors.

        Args:
            query_emb (List[float]): Query embedding vector.
            project_id (str): Project identifier.
            top_k (int): Number of results to return.

        Returns:
            List[Tuple[str, float]]: List of (vector ID, similarity score) pairs.

        Example:
            >>> results = store.similarity_search([0.1, 0.2, ...], "proj1", top_k=3)
        """
        cur = self.conn.execute("SELECT id, embedding FROM vectors WHERE project_id=?", (project_id,))
        results = []
        q = np.array(query_emb, dtype=np.float32)
        for row in cur:
            vec_id, emb_bytes = row
            v = np.frombuffer(emb_bytes, dtype=np.float32)
            # Cosine similarity
            sim = float(np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v) + 1e-8))
            results.append((vec_id, sim))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_snippet(self, vec_id: str) -> str:
        """
        Placeholder: In a real system, fetch the actual snippet for the chunk.
        For now, return the chunk id as a stand-in.

        Args:
            vec_id (str): Vector ID.

        Returns:
            str: Placeholder snippet (vector ID).
        """
        # In future, store and retrieve snippet from a separate table
        return vec_id

    def close(self):
        """
        Close the database connection.

        Example:
            >>> store.close()
        """
        self.conn.close()
