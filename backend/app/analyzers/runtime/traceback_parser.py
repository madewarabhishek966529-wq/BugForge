import re
from typing import Dict, Any, Optional

class TracebackParser:
    """
    Parses standard Python tracebacks from stderr text to extract:
    - Exception type
    - Exception message
    - Stack trace
    - File path
    - Line number
    - Function name
    """
    def parse(self, stderr_text: str) -> Optional[Dict[str, Any]]:
        if not stderr_text or "Traceback (most recent call last):" not in stderr_text:
            return None

        lines = stderr_text.strip().splitlines()
        
        # Exception type and message are typically on the last line
        last_line = lines[-1].strip() if lines else ""
        if ":" in last_line:
            exc_type, exc_msg = last_line.split(":", 1)
            exc_type = exc_type.strip()
            exc_msg = exc_msg.strip()
        else:
            exc_type = last_line
            exc_msg = ""

        # Parse stack frames (File "...", line ..., in ...)
        frame_pattern = re.compile(r'File "(?P<file>.+?)", line (?P<line>\d+)(?:, in (?P<func>.+))?')
        
        last_file = None
        last_line_no = None
        last_func = None

        for line in lines:
            match = frame_pattern.search(line)
            if match:
                last_file = match.group("file")
                last_line_no = int(match.group("line"))
                last_func = match.group("func")

        return {
            "error_type": exc_type,
            "message": exc_msg,
            "file_path": last_file,
            "line_number": last_line_no,
            "function_name": last_func,
            "stack_trace": stderr_text
        }
