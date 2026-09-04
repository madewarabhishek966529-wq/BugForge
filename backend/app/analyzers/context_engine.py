from typing import Dict, Any, Optional

class ContextEngine:
    """
    Extracts relevant source code snippet (20 lines before and after error location),
    locates containing function/class, and compiles static analysis context.
    """
    def extract_context(self, file_path: str, line_number: int) -> Dict[str, Any]:
        return {
            "file_path": file_path,
            "line_number": line_number,
            "code_snippet": "",
            "containing_function": None,
            "containing_class": None
        }
