import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

class PythonRunner:
    def __init__(self, python_executable: Optional[str] = None, timeout: Optional[int] = None):
        self.python_executable = python_executable or settings.PYTHON_EXECUTABLE
        self.timeout = timeout or settings.RUNTIME_TIMEOUT

    def _get_clean_env(self) -> Dict[str, str]:
        """
        Prepares a sanitized environment dictionary by stripping sensitive keys
        (like AI_API_KEY, secrets) to prevent accidental leakage to subprocesses.
        """
        env = os.environ.copy()
        sensitive_keys = ["AI_API_KEY", "SECRET_KEY", "POSTGRES_PASSWORD", "AWS_SECRET_ACCESS_KEY"]
        for key in sensitive_keys:
            env.pop(key, None)
        return env

    def run_script(
        self,
        project_path: str,
        entry_point: str,
        args: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes a local Python script using subprocess.Popen with configurable timeout.
        """
        proj_dir = Path(project_path).resolve()
        if not proj_dir.exists() or not proj_dir.is_dir():
            return {
                "stdout": "",
                "stderr": f"Invalid project directory: {project_path}",
                "exit_code": -1,
                "timed_out": False,
                "error": f"Invalid project directory: {project_path}"
            }

        script_path = (proj_dir / entry_point).resolve()
        # Security check: Ensure target script is within project directory
        try:
            script_path.relative_to(proj_dir)
        except ValueError:
            return {
                "stdout": "",
                "stderr": f"Security Violation: Target script '{entry_point}' is outside project directory.",
                "exit_code": -1,
                "timed_out": False,
                "error": "Security Violation: Script outside project directory."
            }

        if not script_path.exists() or not script_path.is_file():
            return {
                "stdout": "",
                "stderr": f"Script not found: {script_path}",
                "exit_code": -1,
                "timed_out": False,
                "error": f"Script not found: {entry_point}"
            }

        exec_timeout = timeout or self.timeout
        cmd = [self.python_executable, str(script_path)] + (args or [])
        clean_env = self._get_clean_env()

        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(proj_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=clean_env
            )
            
            stdout, stderr = process.communicate(timeout=exec_timeout)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode,
                "timed_out": False,
                "error": None
            }
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return {
                "stdout": stdout,
                "stderr": (stderr or "") + f"\n[Process killed: Exceeded timeout of {exec_timeout}s]",
                "exit_code": -1,
                "timed_out": True,
                "error": f"Execution timed out after {exec_timeout} seconds."
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "timed_out": False,
                "error": str(e)
            }
