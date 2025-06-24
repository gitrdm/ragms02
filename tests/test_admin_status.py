from ragms02.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "projects" in data
    assert "documents_indexed" in data
    assert "last_ingest" in data

def test_list_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data

def test_list_project_sources():
    # Insert a dummy project and source for test
    client.post("/ingest/notify", json={
        "project_id": "test-proj",
        "events": [{"path": "src/test.py", "event_type": "created", "timestamp": "2025-06-24T12:34:56Z", "content": "print('hi')"}]
    })
    response = client.get("/projects/test-proj/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data

def test_get_logs():
    response = client.get("/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data

def test_get_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
