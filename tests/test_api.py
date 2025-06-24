import pytest
from fastapi.testclient import TestClient
from ragms02.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ingest_notify():
    payload = {
        "project_id": "test-project",
        "events": [
            {
                "path": "src/main.py",
                "event_type": "modified",
                "timestamp": "2025-06-24T12:34:56Z"
            }
        ]
    }
    response = client.post("/ingest/notify", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_ingest_notify_multiple_chunks():
    payload = {
        "project_id": "test-project",
        "events": [
            {
                "path": "src/longfile.txt",
                "event_type": "modified",
                "timestamp": "2025-06-24T12:34:56Z",
                "content": "A" * 1000  # Should create multiple chunks
            }
        ]
    }
    response = client.post("/ingest/notify", json=payload)
    assert response.status_code == 200
    assert response.json()["processed"] > 1
