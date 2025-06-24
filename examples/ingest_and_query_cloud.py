"""
Example: Ingest code and query using a cloud-based LLM (OpenAI API)
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
print("Ingest status:", resp.status_code)
print("Ingest raw response:", resp.text)
try:
    print("Ingest response (parsed JSON):", resp.json())
except Exception as e:
    print("Failed to parse ingest response as JSON:", e)

# Query the LLM about the code using a cloud model (e.g., gpt-3.5-turbo)
query_payload = {
    "query": "What does the multiply function do in sample_code.py?",
    "projects": [PROJECT_ID],
    "model": "gemini-1.5-flash"
}
query_resp = requests.post(f"{API_URL}/query", json=query_payload)
print("Query status:", query_resp.status_code)
print("Query raw response:", query_resp.text)
try:
    print("Query response (parsed JSON):", query_resp.json())
except Exception as e:
    print("Failed to parse query response as JSON:", e)
