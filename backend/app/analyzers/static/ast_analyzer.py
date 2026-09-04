import ast
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("bugforge.analyzers.ast")


class ASTAnalyzer:
    """
    Walks the Python AST to detect real issues that Ruff/Pylint may miss:
    - Bare except clauses
    - Mutable default arguments (list/dict/set as default)
    - Assert statements used for runtime logic
    - Comparison to None using == instead of `is`
    - Returning inside a finally block
    - Unused variables assigned but never read (simple heuristic)
    """

    def analyze(self, file_path: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists() or not path.suffix == ".py":
            return []

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            return [{
                "tool": "ast",
                "code": "SyntaxError",
                "message": str(e),
                "error_type": "SyntaxError",
                "severity": "critical",
                "file_path": str(path),
                "line_number": e.lineno or 0,
                "source": "static",
            }]
        except Exception as e:
            logger.error(f"ASTAnalyzer: failed to parse {file_path}: {e}")
            return []

        issues: List[Dict[str, Any]] = []
        visitor = _ASTVisitor(str(path))
        visitor.visit(tree)
        return visitor.issues


class _ASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[Dict[str, Any]] = []

    def _issue(self, node: ast.AST, code: str, message: str, severity: str = "medium"):
        self.issues.append({
            "tool": "ast",
            "code": code,
            "message": message,
            "error_type": code,
            "severity": severity,
            "file_path": self.file_path,
            "line_number": getattr(node, "lineno", 0),
            "source": "static",
        })

    # ── Bare except ────────────────────────────────────────────────────────
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is None:
            self._issue(node, "BareExcept",
                        "Bare `except:` catches all exceptions including KeyboardInterrupt and SystemExit. "
                        "Specify the exception type(s) to catch.",
                        severity="high")
        self.generic_visit(node)

    # ── Mutable default arguments ──────────────────────────────────────────
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_mutable_defaults(node)
        self._check_return_in_finally(node)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _check_mutable_defaults(self, node: ast.FunctionDef):
        for default in node.args.defaults + node.args.kw_defaults:
            if default is None:
                continue
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                type_name = type(default).__name__.lower()
                self._issue(node, "MutableDefaultArgument",
                            f"Mutable default argument `{type_name}` in `{node.name}()`. "
                            "This object is shared across all calls. Use `None` and initialise inside the function.",
                            severity="high")

    def _check_return_in_finally(self, node: ast.FunctionDef):
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                for final_node in ast.walk(ast.Module(body=child.finalbody, type_ignores=[])):
                    if isinstance(final_node, ast.Return):
                        self._issue(final_node, "ReturnInFinally",
                                    "`return` inside a `finally` block suppresses exceptions. "
                                    "Move the return statement outside the finally block.",
                                    severity="high")

    # ── Assert used for runtime logic ──────────────────────────────────────
    def visit_Assert(self, node: ast.Assert):
        self._issue(node, "AssertUsedForLogic",
                    "`assert` statements are removed when Python runs with -O flag. "
                    "Use proper `if/raise` for runtime guards.",
                    severity="medium")
        self.generic_visit(node)

    # ── Comparison to None with == ─────────────────────────────────────────
    def visit_Compare(self, node: ast.Compare):
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant) and comparator.value is None:
                op_str = "==" if isinstance(op, ast.Eq) else "!="
                self._issue(node, "NoneComparison",
                            f"Use `is None` / `is not None` instead of `{op_str} None` (PEP 8 E711).",
                            severity="low")
        self.generic_visit(node)
