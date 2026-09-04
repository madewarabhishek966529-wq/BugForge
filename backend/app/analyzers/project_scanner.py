import os
from pathlib import Path
from typing import List, Dict, Any

IGNORED_DIRS = {
    ".git", "venv", ".venv", "env", "__pycache__",
    "node_modules", "build", "dist", ".pytest_cache", ".ruff_cache"
}

class ProjectScanner:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def scan(self) -> Dict[str, Any]:
        if not self.project_path.exists() or not self.project_path.is_dir():
            raise ValueError(f"Invalid directory path: {self.project_path}")

        py_files = []
        entry_points = []

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    rel_path = str(full_path.relative_to(self.project_path))
                    py_files.append(rel_path)
                    if file in ("main.py", "app.py", "run.py", "cli.py"):
                        entry_points.append(rel_path)

        return {
            "files_found": len(py_files),
            "file_map": py_files,
            "entry_points": entry_points
        }
