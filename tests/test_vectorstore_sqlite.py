import os
import tempfile
from ragms02.vectorstore.sqlite import VectorStore

def test_add_and_get_vector():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    try:
        store = VectorStore(db_path)
        store.add_vector("vec1", "proj1", "tag1", b"\x01\x02\x03")
        result = store.get_vector("vec1")
        assert result == b"\x01\x02\x03"
        store.close()
    finally:
        os.remove(db_path)
