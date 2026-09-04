import subprocess
import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("bugforge.analyzers.ruff")

# Map Ruff rule prefixes to severity
_SEVERITY_MAP = {
    "E": "high",     # pycodestyle errors
    "F": "high",     # pyflakes (undefined names, unused imports)
    "W": "medium",   # pycodestyle warnings
    "N": "low",      # pep8 naming
    "B": "medium",   # flake8-bugbear
    "C": "low",      # convention
    "I": "low",      # isort
    "UP": "low",     # pyupgrade
    "ANN": "low",    # annotations
    "S": "high",     # security (bandit)
    "T": "medium",   # type checking
    "RUF": "medium", # Ruff-specific
}


def _map_severity(code: str) -> str:
    prefix = "".join(c for c in code if c.isalpha())
    for key in _SEVERITY_MAP:
        if prefix.startswith(key):
            return _SEVERITY_MAP[key]
    return "low"


class RuffAnalyzer:
    def analyze(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Runs Ruff on the project directory and returns a list of structured findings.
        """
        path = Path(project_path).resolve()
        if not path.exists():
            logger.warning(f"RuffAnalyzer: path does not exist: {path}")
            return []

        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "ruff", "check",
                    str(path),
                    "--output-format", "json",
                    "--no-cache",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            raw = result.stdout.strip()
            if not raw:
                return []

            findings = json.loads(raw)
            issues: List[Dict[str, Any]] = []
            for f in findings:
                code = f.get("code") or "RUFF"
                msg = f.get("message", "")
                loc = f.get("location", {})
                filepath = f.get("filename", "")
                line = loc.get("row", 0)

                issues.append({
                    "tool": "ruff",
                    "code": code,
                    "message": msg,
                    "error_type": code,
                    "severity": _map_severity(code),
                    "file_path": filepath,
                    "line_number": line,
                    "source": "static",
                })
            return issues

        except subprocess.TimeoutExpired:
            logger.error("RuffAnalyzer: timed out")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"RuffAnalyzer: JSON parse error: {e}")
            return []
        except Exception as e:
            logger.error(f"RuffAnalyzer: unexpected error: {e}")
            return []
