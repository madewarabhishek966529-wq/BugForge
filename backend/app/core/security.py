"""
BugForge Security Core module.
Provides helper functions for path validation and execution safety.
"""
import os
from pathlib import Path

def is_safe_project_path(path_str: str) -> bool:
    """
    Validates that a project path exists and is a valid directory.
    """
    try:
        path = Path(path_str).resolve()
        return path.exists() and path.is_dir()
    except Exception:
        return False
