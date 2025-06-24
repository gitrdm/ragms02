from unittest.mock import patch
from ragms02.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@patch("ragms02.llm.ollama.OllamaLLM.generate")
def test_query_llm(mock_generate):
    mock_generate.return_value = "Mocked LLM response"
    payload = {
        "query": "What is RAG?",
        "projects": ["proj1"],
        "model": "llama2"
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Mocked LLM response"
    assert data["error"] is None or data["error"] == ""
