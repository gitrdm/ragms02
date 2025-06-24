"""
Example: Ingest code and query using a local LLM (Ollama)
"""
import base64
import requests
from datetime import datetime

API_URL = "http://localhost:8001"
PROJECT_ID = "example-project"
CODE_PATH = "examples/sample_code.py"

# Read and encode the code file
with open(CODE_PATH, "r") as f:
    code_content = f.read()
    code_b64 = base64.b64encode(code_content.encode("utf-8")).decode("utf-8")

# Ingest the code file
payload = {
    "project_id": PROJECT_ID,
    "events": [
        {
            "path": CODE_PATH,
            "event_type": "created",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "content": code_content,
        }
    ]
}
resp = requests.post(f"{API_URL}/ingest/notify", json=payload)
print("Ingest response:", resp.json())

# Query the LLM about the code
query_payload = {
    "query": "What does the add function do in sample_code.py?",
    "projects": [PROJECT_ID],
    "model": "llama2"
}
query_resp = requests.post(f"{API_URL}/query", json=query_payload)
print("Query response (local LLM):", query_resp.json())
