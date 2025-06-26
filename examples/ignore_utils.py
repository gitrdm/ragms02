"""
ignore_utils.py - Shared ignore pattern loader for RAGMS02

This utility loads .ragignore (gitignore-style) patterns and provides a function to check if a path should be ignored.
"""
import os
import pathspec

def load_ignore_patterns(ignore_file=".ragignore"):
    if not os.path.exists(ignore_file):
        return pathspec.PathSpec.from_lines("gitwildmatch", [])
    with open(ignore_file) as f:
        patterns = f.read().splitlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def is_ignored(path, spec):
    # path should be relative to the root being scanned
    return spec.match_file(path)
