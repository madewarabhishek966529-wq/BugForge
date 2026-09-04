import subprocess
import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("bugforge.analyzers.pylint")

# Pylint message types → severity
_TYPE_SEVERITY = {
    "error":      "high",
    "fatal":      "critical",
    "warning":    "medium",
    "convention": "low",
    "refactor":   "low",
    "information":"low",
}


class PylintAnalyzer:
    def analyze(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Runs Pylint on all Python files in the project and returns structured findings.
        """
        path = Path(project_path).resolve()
        if not path.exists():
            logger.warning(f"PylintAnalyzer: path does not exist: {path}")
            return []

        # Collect all .py files (respecting ignored dirs)
        ignored = {".git", "venv", ".venv", "env", "__pycache__",
                   "node_modules", "build", "dist", ".pytest_cache"}
        py_files: List[str] = []
        for f in path.rglob("*.py"):
            if not any(part in ignored for part in f.parts):
                py_files.append(str(f))

        if not py_files:
            return []

        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "pylint",
                    *py_files,
                    "--output-format=json",
                    "--score=no",
                    "--disable=C0114,C0115,C0116",  # suppress missing docstring noise
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            raw = result.stdout.strip()
            if not raw:
                return []

            findings = json.loads(raw)
            issues: List[Dict[str, Any]] = []
            for f in findings:
                msg_type = f.get("type", "warning")
                issues.append({
                    "tool": "pylint",
                    "code": f.get("message-id", ""),
                    "message": f.get("message", ""),
                    "error_type": f.get("symbol", f.get("message-id", "pylint")),
                    "severity": _TYPE_SEVERITY.get(msg_type, "medium"),
                    "file_path": f.get("path", ""),
                    "line_number": f.get("line", 0),
                    "source": "static",
                })
            return issues

        except subprocess.TimeoutExpired:
            logger.error("PylintAnalyzer: timed out")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"PylintAnalyzer: JSON parse error: {e}")
            return []
        except Exception as e:
            logger.error(f"PylintAnalyzer: unexpected error: {e}")
            return []
