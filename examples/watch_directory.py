"""
Example: Watch a directory for file changes using the RAGMS02 file watcher
"""
from ragms02.watcher.watcher import WatcherConfig, FileWatcher

if __name__ == "__main__":
    # Change this path to the directory you want to watch
    config = WatcherConfig(path="./my_project")
    watcher = FileWatcher(config)
    watcher.start()
