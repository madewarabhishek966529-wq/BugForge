from typing import Dict, Any, Optional

class PythonRunner:
    def run_script(self, project_path: str, entry_point: str, timeout: int = 30) -> Dict[str, Any]:
        return {
            "stdout": "",
            "stderr": "",
            "exit_code": 0,
            "timed_out": False
        }
