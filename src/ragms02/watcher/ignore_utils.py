"""
ignore_utils.py - Shared ignore pattern loader for RAGMS02

This utility loads .ragignore (gitignore-style) patterns and provides a function to check if a path should be ignored.
"""
import os
import pathspec
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def load_ignore_patterns(ignore_file: Optional[str] = None, root_dir: Optional[str] = None) -> pathspec.PathSpec:
    """
    Load ignore patterns from a .ragignore file. If ignore_file is not absolute, it is joined with root_dir.
    Returns a PathSpec object. If the file does not exist, returns an empty spec.
    """
    if ignore_file is None:
        ignore_file = ".ragignore"
    if root_dir and not os.path.isabs(ignore_file):
        ignore_file = os.path.join(root_dir, ignore_file)
    logger.debug(f"Loading ignore patterns from: {os.path.abspath(ignore_file)}")
    if not os.path.exists(ignore_file):
        logger.debug("Ignore file does not exist.")
        return pathspec.PathSpec.from_lines("gitwildmatch", [])
    with open(ignore_file) as f:
        patterns = f.read().splitlines()
    logger.debug(f"Loaded ignore patterns: {patterns}")
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def is_ignored(path: str, spec: pathspec.PathSpec) -> bool:
    """
    Check if a given path (relative to project root, POSIX style) should be ignored.
    """
    norm_path = to_posix_path(path)
    result = spec.match_file(norm_path)
    logger.debug(f"Checking ignore for path '{norm_path}': {result}")
    return result

def to_posix_path(path: str) -> str:
    """
    Convert a path to POSIX style (forward slashes), relative if possible.
    """
    return os.path.normpath(path).replace(os.sep, "/")

def relpath_from_root(path: str, root: str) -> str:
    """
    Get the POSIX-style path of 'path' relative to 'root'.
    """
    rel = os.path.relpath(path, root)
    return to_posix_path(rel)
