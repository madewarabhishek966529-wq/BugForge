import os
import sys
import tempfile
from pathlib import Path
from backend.app.analyzers.runtime.runner import PythonRunner

def test_runner_successful_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        script = Path(tmpdir) / "test_main.py"
        script.write_text("print('Hello BugForge!')\n")

        runner = PythonRunner(python_executable=sys.executable, timeout=5)
        res = runner.run_script(tmpdir, "test_main.py")

        assert res["exit_code"] == 0
        assert res["timed_out"] is False
        assert "Hello BugForge!" in res["stdout"]
        assert res["stderr"] == ""

def test_runner_timeout_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        script = Path(tmpdir) / "test_sleep.py"
        script.write_text("import time\ntime.sleep(10)\n")

        runner = PythonRunner(python_executable=sys.executable, timeout=1)
        res = runner.run_script(tmpdir, "test_sleep.py")

        assert res["timed_out"] is True
        assert res["exit_code"] == -1
        assert "timeout" in res["stderr"].lower()

def test_runner_environment_scrubbing():
    with tempfile.TemporaryDirectory() as tmpdir:
        script = Path(tmpdir) / "test_env.py"
        script.write_text("import os\nprint('KEY:' + str(os.environ.get('AI_API_KEY')))\n")

        os.environ["AI_API_KEY"] = "super-secret-key-12345"
        try:
            runner = PythonRunner(python_executable=sys.executable, timeout=5)
            res = runner.run_script(tmpdir, "test_env.py")

            assert "super-secret-key-12345" not in res["stdout"]
            assert "KEY:None" in res["stdout"]
        finally:
            os.environ.pop("AI_API_KEY", None)

def test_runner_outside_directory_security():
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = PythonRunner(python_executable=sys.executable, timeout=5)
        res = runner.run_script(tmpdir, "../outside.py")

        assert res["exit_code"] == -1
        assert "Security Violation" in res["stderr"]
