import ast
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger("bugforge.analyzers.context_engine")

CONTEXT_LINES = 20  # lines before and after the error line


class ContextEngine:
    """
    Given a file path and a line number, extracts:
    - A numbered code snippet (CONTEXT_LINES before and after the error)
    - The enclosing function name (if any)
    - The enclosing class name (if any)
    """

    def extract_context(self, file_path: str, line_number: int) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "file_path": file_path,
            "line_number": line_number,
            "code_snippet": "",
            "containing_function": None,
            "containing_class": None,
        }

        if not file_path:
            return result

        path = Path(file_path)
        if not path.exists():
            return result

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning(f"ContextEngine: cannot read {file_path}: {e}")
            return result

        lines = source.splitlines()
        total = len(lines)
        target = max(1, line_number) - 1  # zero-indexed

        start = max(0, target - CONTEXT_LINES)
        end   = min(total, target + CONTEXT_LINES + 1)

        # Build numbered snippet with arrow on error line
        snippet_lines: List[str] = []
        for i in range(start, end):
            lineno = i + 1
            marker = ">>>" if i == target else "   "
            snippet_lines.append(f"{lineno:4d} {marker} {lines[i]}")
        result["code_snippet"] = "\n".join(snippet_lines)

        # Walk AST to find enclosing function and class
        try:
            tree = ast.parse(source, filename=str(path))
            result["containing_function"], result["containing_class"] = \
                _find_enclosing(tree, line_number)
        except SyntaxError:
            pass

        return result


def _find_enclosing(tree: ast.AST, line: int):
    """Returns (function_name, class_name) of the innermost scope containing `line`."""
    func_name: Optional[str] = None
    class_name: Optional[str] = None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", None) or node.lineno
            if node.lineno <= line <= end:
                func_name = node.name
        elif isinstance(node, ast.ClassDef):
            end = getattr(node, "end_lineno", None) or node.lineno
            if node.lineno <= line <= end:
                class_name = node.name

    return func_name, class_name
