"""
Example: File watcher using .ragignore for exclusion (RAGMS02)

This script demonstrates how to use the shared ignore utility with Watchdog to exclude files/directories
matching patterns in .ragignore, ensuring consistent behavior with bulk ingestion.
"""
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ignore_utils import load_ignore_patterns, is_ignored

WATCH_PATH = "./my_project"  # Change to your project directory
spec = load_ignore_patterns(".ragignore")

class IgnoreRagignoreHandler(FileSystemEventHandler):
    def dispatch(self, event):
        # Only handle file/directory events not ignored by .ragignore
        rel_path = os.path.relpath(event.src_path, WATCH_PATH)
        if is_ignored(rel_path, spec):
            return
        super().dispatch(event)

    def on_created(self, event):
        print(f"Created: {event.src_path}")

    def on_modified(self, event):
        print(f"Modified: {event.src_path}")

    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")

    def on_moved(self, event):
        print(f"Moved: {event.src_path} -> {event.dest_path}")

if __name__ == "__main__":
    observer = Observer()
    handler = IgnoreRagignoreHandler()
    observer.schedule(handler, path=WATCH_PATH, recursive=True)
    observer.start()
    print(f"Watching '{WATCH_PATH}' (excluding patterns in .ragignore). Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
