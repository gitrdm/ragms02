from typing import List
import numpy as np

def embed_text(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text.

    This is a placeholder implementation. In real use, replace with a call to an embedding model (e.g., sentence-transformers, OpenAI, etc.).

    Args:
        text (str): Input text to embed.

    Returns:
        List[float]: Embedding vector of fixed size (384).

    Example:
        >>> vec = embed_text("Hello world!")
        >>> len(vec)
        384
    """
    np.random.seed(hash(text) % 2**32)
    return np.random.rand(384).tolist()
