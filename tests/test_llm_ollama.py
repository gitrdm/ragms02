import pytest
from unittest.mock import patch
from ragms02.llm.ollama import OllamaLLM

@patch("ragms02.llm.ollama.requests.post")
def test_generate_calls_ollama_api(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": "Hello, world!"}
    llm = OllamaLLM(base_url="http://localhost:11434")
    result = llm.generate("Say hello", model="llama2")
    assert result == "Hello, world!"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "llama2" in str(kwargs["json"]) or "llama2" in str(kwargs)
