import sqlite3
import tempfile
import os
import pytest

@pytest.fixture
def temp_db():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()
    os.remove(db_path)

def test_sqlite_db_connection(temp_db):
    cur = temp_db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vectors (id TEXT PRIMARY KEY, embedding BLOB)")
    cur.execute("INSERT INTO vectors (id, embedding) VALUES (?, ?)", ("test-id", b"\x00\x01\x02"))
    temp_db.commit()
    cur.execute("SELECT id, embedding FROM vectors WHERE id=?", ("test-id",))
    row = cur.fetchone()
    assert row[0] == "test-id"
    assert row[1] == b"\x00\x01\x02"
