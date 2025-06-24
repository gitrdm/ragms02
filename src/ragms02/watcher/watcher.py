import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logger = logging.getLogger("ragms02.watcher")

class WatcherConfig:
    """
    Configuration for the file watcher.

    Args:
        path (str): Directory path to watch.

    Example:
        >>> config = WatcherConfig(path="./data")
    """
    def __init__(self, path: str = "."):
        self.path = path

class ChangeHandler(FileSystemEventHandler):
    """
    Handles file system events and logs them.
    """
    def on_any_event(self, event):
        """
        Log any file system event.

        Args:
            event: Watchdog event object.
        """
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

    def start(self):
        """
        Start watching the configured directory for file changes.
        """
        event_handler = ChangeHandler()
        self.observer.schedule(event_handler, self.config.path, recursive=True)
        self.observer.start()
        logger.info(f"Started watching: {self.config.path}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = WatcherConfig(path="./")
    watcher = FileWatcher(config)
    watcher.start()
