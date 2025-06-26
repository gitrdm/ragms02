"""
Example: Watch a project directory for changes, using .ragignore for exclusion.

This script demonstrates how to use the Watchdog-based file watcher from this project
and exclude files/directories based on patterns in .ragignore, ensuring consistency
with bulk ingestion and other watcher examples.
"""
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ignore_utils import load_ignore_patterns, is_ignored

WATCH_PATH = "./my_project"  # Change to your project directory
RAGIGNORE_PATH = os.path.join(WATCH_PATH, ".ragignore")

spec = load_ignore_patterns(RAGIGNORE_PATH)

class RagignoreHandler(FileSystemEventHandler):
    def dispatch(self, event):
        # Only handle file/directory events not ignored by .ragignore
        src_path = str(event.src_path)
        rel_path = os.path.relpath(os.path.abspath(src_path), os.path.abspath(WATCH_PATH))
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
    handler = RagignoreHandler()
    observer.schedule(handler, path=WATCH_PATH, recursive=True)
    observer.start()
    print(f"Watching '{WATCH_PATH}' (excluding patterns in .ragignore). Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
