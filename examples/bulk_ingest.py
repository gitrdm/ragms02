"""
Example: Bulk import (recursive directory ingestion) for RAGMS02, respecting .ragignore
"""
import os
import requests
from ignore_utils import load_ignore_patterns, is_ignored

API_URL = "http://localhost:8000/ingest/notify"
PROJECT_ID = "example-project"
ROOT_DIR = "./my_project"  # Change to your directory

spec = load_ignore_patterns(".ragignore")
events = []
for root, dirs, files in os.walk(ROOT_DIR):
    # Filter out ignored directories in-place
    dirs[:] = [d for d in dirs if not is_ignored(os.path.relpath(os.path.join(root, d), ROOT_DIR), spec)]
    for file in files:
        rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
        if is_ignored(rel_path, spec):
            continue
        events.append({"path": rel_path, "event_type": "created"})

payload = {
    "project_id": PROJECT_ID,
    "events": events
}

resp = requests.post(API_URL, json=payload)
print("Bulk ingest status:", resp.status_code)
print("Bulk ingest response:", resp.json())
