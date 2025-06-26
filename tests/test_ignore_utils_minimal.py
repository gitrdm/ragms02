"""
Minimal test for ignore_utils.py root-level file matching with pathspec.
"""
import os
import sys
import tempfile
# Add src/ to sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from ragms02.watcher.ignore_utils import load_ignore_patterns, is_ignored

def test_ignore_patterns_for_root_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        ragignore_path = os.path.join(tmpdir, ".ragignore")
        # Try various patterns
        patterns = [
            "file.txt", "./file.txt", "/file.txt", "**/file.txt"
        ]
        with open(ragignore_path, "w") as f:
            f.write("\n".join(patterns))
        spec = load_ignore_patterns(ragignore_path)
        # Test various path forms
        assert is_ignored("file.txt", spec), "'file.txt' should be ignored by at least one pattern"
        assert is_ignored("./file.txt", spec), "'./file.txt' should be ignored by at least one pattern"
        assert is_ignored("subdir/file.txt", spec), "'subdir/file.txt' should be ignored by '**/file.txt'"
        assert not is_ignored("file.md", spec), "'file.md' should not be ignored"

if __name__ == "__main__":
    test_ignore_patterns_for_root_file()
    print("Minimal ignore_utils test passed.")
