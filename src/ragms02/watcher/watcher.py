import time
import os
import threading
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from .ignore_utils import load_ignore_patterns, is_ignored, relpath_from_root

logger = logging.getLogger("ragms02.watcher")

RAGIGNORE_FILE = ".ragignore"
RAGS_API_URL = os.environ.get("RAGS_API_URL", "http://localhost:8000/ingest/notify")
PROJECT_ID = os.environ.get("RAGS_PROJECT_ID", "default-project")

class WatcherConfig:
    """
    Configuration for the file watcher.

    Args:
        path (str): Directory path to watch.

    Example:
        >>> config = WatcherConfig(path="./data")
    """
    def __init__(self, path: str = ".", ignore_file: str = ".ragignore"):
        self.path = os.path.abspath(path)
        self.ignore_file = ignore_file

class ChangeHandler(FileSystemEventHandler):
    """
    Handles file system events and logs them.
    """
    def __init__(self, watch_path, ignore_spec):
        super().__init__()
        self.watch_path = watch_path
        self.ignore_spec = ignore_spec

    def on_any_event(self, event):
        rel_path = relpath_from_root(event.src_path, self.watch_path)
        ignore_status = is_ignored(rel_path, self.ignore_spec)
        logger.debug(f"EVENT CHECK: rel_path='{rel_path}' ignore_status={ignore_status}")
        if ignore_status:
            return
        logger.info(f"Event: {event.event_type} - {event.src_path}")

class FileWatcher:
    """
    File system watcher that monitors a directory for changes.

    Example:
        >>> config = WatcherConfig(path="./")
        >>> watcher = FileWatcher(config)
        >>> watcher.start()
    """
    def __init__(self, config: WatcherConfig):
        """
        Initialize the FileWatcher.

        Args:
            config (WatcherConfig): Watcher configuration.
        """
        self.config = config
        self.observer = Observer()
        self.ignore_spec = load_ignore_patterns(ignore_file=self.config.ignore_file, root_dir=self.config.path)
        self._ragignore_mtime = self._get_ragignore_mtime()
        self._stop_event = threading.Event()
        self._prev_ignored = self._get_ignored_set(self.ignore_spec)

    def _get_ignored_set(self, ignore_spec):
        ignored = set()
        for root, dirs, files in os.walk(self.config.path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = relpath_from_root(abs_path, self.config.path)
                # Add debug logging for rel_path and ignore status
                ignore_status = is_ignored(rel_path, ignore_spec)
                logger.debug(f"CHECK: rel_path='{rel_path}' ignore_status={ignore_status}")
                if ignore_status:
                    logger.debug(f"IGNORED (pattern match): {rel_path}")
                    ignored.add(rel_path)
                else:
                    logger.debug(f"NOT IGNORED: {rel_path}")
        return ignored

    def _get_ragignore_mtime(self):
        ragignore_path = os.path.join(self.config.path, self.config.ignore_file)
        return os.path.getmtime(ragignore_path) if os.path.exists(ragignore_path) else None

    def _monitor_ragignore(self):
        while not self._stop_event.is_set():
            time.sleep(2)
            mtime = self._get_ragignore_mtime()
            if mtime != self._ragignore_mtime:
                logger.info("Detected .ragignore change. Reloading ignore patterns and sending delete events.")
                prev_ignored = self._prev_ignored  # snapshot before reload
                new_spec = load_ignore_patterns(ignore_file=self.config.ignore_file, root_dir=self.config.path)
                new_ignored = self._get_ignored_set(new_spec)
                newly_ignored = new_ignored - prev_ignored
                self.ignore_spec = new_spec
                self._ragignore_mtime = mtime
                self._send_delete_for_ignored(newly_ignored)
                self._prev_ignored = new_ignored

    def _send_delete_for_ignored(self, ignored_set=None):
        events = []
        if ignored_set is None:
            ignored_set = self._get_ignored_set(self.ignore_spec)
        for rel_path in ignored_set:
            logger.info(f"Sending delete event for: {rel_path}")
            events.append({"path": rel_path, "event_type": "deleted"})
        if events:
            payload = {"project_id": PROJECT_ID, "events": events}
            try:
                resp = requests.post(RAGS_API_URL, json=payload)
                logger.info(f"Sent delete events for ignored files. Status: {resp.status_code}")
            except Exception as e:
                logger.error(f"Failed to send delete events: {e}")

    def start(self):
        """
        Start watching the configured directory for file changes.
        """
        event_handler = ChangeHandler(self.config.path, self.ignore_spec)
        self.observer.schedule(event_handler, self.config.path, recursive=True)
        self.observer.start()
        logger.info(f"Started watching: {self.config.path}")
        # Start .ragignore monitor thread
        monitor_thread = threading.Thread(target=self._monitor_ragignore, daemon=True)
        monitor_thread.start()
        try:
            while not self._stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self._stop_event.set()
            self.observer.stop()
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = WatcherConfig(path="./")
    watcher = FileWatcher(config)
    watcher.start()
