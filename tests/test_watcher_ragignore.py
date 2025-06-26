"""
Test: FileWatcher and .ragignore integration

These tests verify that the watcher loads .ragignore, ignores files as expected, and triggers delete events when .ragignore is added or changed.
"""
import os
import sys
import tempfile
import shutil
import time
import threading
import requests
import pytest
from unittest import mock

# Ensure src/ is on sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from ragms02.watcher.watcher import FileWatcher, WatcherConfig

@pytest.fixture
def temp_project_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.fixture
def patch_requests_post():
    with mock.patch("requests.post") as m:
        yield m

def write_file(path, content="test"):
    with open(path, "w") as f:
        f.write(content)

@pytest.mark.timeout(10)
def test_watcher_respects_ragignore(temp_project_dir, patch_requests_post):
    # Setup project dir and .ragignore
    project = temp_project_dir
    ragignore = os.path.join(project, ".ragignore")
    write_file(ragignore, "ignored_dir/\n*.skip\n")
    os.makedirs(os.path.join(project, "ignored_dir"))
    write_file(os.path.join(project, "ignored_dir", "foo.txt"))
    write_file(os.path.join(project, "file.skip"))
    write_file(os.path.join(project, "file.txt"))

    # Start watcher in a thread, pass ignore_file explicitly
    config = WatcherConfig(path=project, ignore_file=".ragignore")
    watcher = FileWatcher(config)
    t = threading.Thread(target=watcher.start, daemon=True)
    t.start()
    time.sleep(2)  # Let watcher start

    # Touch a file that should be ignored
    write_file(os.path.join(project, "ignored_dir", "bar.txt"))
    write_file(os.path.join(project, "file.skip"))
    write_file(os.path.join(project, "file.txt"))
    time.sleep(2)

    # Now update .ragignore to ignore file.txt (both root and any depth)
    write_file(ragignore, "ignored_dir/\n*.skip\nfile.txt\n**/file.txt\n")
    time.sleep(4)  # Wait for watcher to reload and send delete

    # Check that requests.post was called with delete for file.txt
    found = False
    for call in patch_requests_post.call_args_list:
        args, kwargs = call
        if kwargs.get("json"):
            events = kwargs["json"].get("events", [])
            for e in events:
                if e["path"].endswith("file.txt") and e["event_type"] == "deleted":
                    found = True
    assert found, "Watcher should send delete event for newly ignored file.txt"

    watcher._stop_event.set()
    t.join(timeout=2)
