import os
import tempfile
import time
import threading
from ragms02.watcher.watcher import FileWatcher, WatcherConfig


def test_file_watcher_detects_file_creation(tmp_path):
    # Setup a temporary directory to watch
    test_dir = tmp_path / "watched"
    test_dir.mkdir()
    config = WatcherConfig(path=str(test_dir))
    events = []

    class TestHandler:
        def __init__(self):
            self.triggered = False
        def on_any_event(self, event):
            events.append(event)
            self.triggered = True

    # Patch the handler in FileWatcher
    from watchdog.events import FileSystemEventHandler
    class PatchedHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            events.append(event)

    watcher = FileWatcher(config)
    watcher.observer._handlers.clear()  # Remove any existing handlers
    watcher.observer.schedule(PatchedHandler(), config.path, recursive=True)

    # Start watcher in a thread
    t = threading.Thread(target=watcher.start, daemon=True)
    t.start()
    time.sleep(1)  # Give the watcher time to start

    # Create a file
    test_file = test_dir / "test.txt"
    with open(test_file, "w") as f:
        f.write("hello")
    time.sleep(1)  # Give the watcher time to detect

    watcher.observer.stop()
    t.join(timeout=2)

    assert any("test.txt" in str(e.src_path) for e in events)
