"""
Example: Watch a project directory for changes, excluding the 'examples' directory.

This script demonstrates how to use the Watchdog-based file watcher from this project
and exclude a specific directory (here, './examples') from being watched/ingested.

You can adapt the ignore logic for other patterns or directories as needed.
"""
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

WATCH_PATH = "./my_project"  # Change to your project directory
EXCLUDE_DIR = "examples"

# Ignore all files and subdirectories under './examples/'
ignore_patterns = [f"{WATCH_PATH}/{EXCLUDE_DIR}/*"]

class ExcludeExamplesHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(ignore_patterns=ignore_patterns, ignore_directories=False)

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
    handler = ExcludeExamplesHandler()
    observer.schedule(handler, path=WATCH_PATH, recursive=True)
    observer.start()
    print(f"Watching '{WATCH_PATH}' (excluding '{EXCLUDE_DIR}/') for changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
