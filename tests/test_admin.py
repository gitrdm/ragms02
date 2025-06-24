from ragms02.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_admin_reset():
    response = client.post("/admin/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reset"
    assert "cleared" in data["message"]

def test_admin_reindex():
    response = client.post("/admin/reindex")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reindexing"
    assert "Reindexing started" in data["message"]
