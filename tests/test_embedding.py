from ragms02.vectorstore.embedding import embed_text

def test_embed_text_returns_vector():
    vec = embed_text("hello world")
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)
    # Deterministic for same input
    vec2 = embed_text("hello world")
    assert vec == vec2
    # Different for different input
    vec3 = embed_text("goodbye")
    assert vec != vec3
