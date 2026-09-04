from typing import Dict, Any, List, Optional


class PromptBuilder:
    """
    Builds a rich, focused prompt for the AI provider from a bug context dictionary.
    Structured to produce evidence-based root-cause analysis with a minimal patch.
    """

    def build_bug_analysis_prompt(self, context: Dict[str, Any]) -> str:
        error_type      = context.get("error_type", "UnknownError")
        message         = context.get("message", "")
        file_path       = context.get("file_path", "unknown")
        line_number     = context.get("line_number", "?")
        function_name   = context.get("function_name") or "module-level"
        class_name      = context.get("containing_class") or ""
        stack_trace     = context.get("stack_trace") or "N/A"
        code_snippet    = context.get("code_snippet") or "N/A"
        static_warnings = context.get("static_warnings") or "None"
        project_name    = context.get("project_name", "Unknown Project")
        source          = context.get("source", "runtime")

        class_info = f"Class: {class_name}\n" if class_name else ""

        return f"""You are BugForge — an expert Python debugging assistant.

Analyze the following bug and provide a precise, evidence-based diagnosis.
Do NOT invent file names or line numbers that are not in the context below.
Distinguish facts (things you can see in the trace) from hypotheses.

=== PROJECT ===
Name: {project_name}
Source: {source} ({"runtime execution" if source == "runtime" else "static analysis"})

=== ERROR ===
Type:     {error_type}
Message:  {message}
File:     {file_path}
Line:     {line_number}
{class_info}Function: {function_name}

=== STACK TRACE ===
{stack_trace}

=== SOURCE CODE (around error location, line numbers shown) ===
{code_snippet}

=== STATIC ANALYSIS WARNINGS (Ruff / Pylint / AST) ===
{static_warnings}
======================

Respond with ONLY a JSON object exactly matching this schema — no markdown, no explanation outside JSON:
{{
  "error_type": "{error_type}",
  "severity": "critical | high | medium | low",
  "confidence": <float 0.0–1.0>,
  "summary": "<one sentence explaining the bug>",
  "root_cause": "<detailed explanation of WHY the bug happens>",
  "facts": ["<fact directly visible in trace or code>", ...],
  "hypotheses": ["<possible but unconfirmed cause>", ...],
  "evidence": [
    {{"file": "<path>", "line": <int>, "reason": "<why this line matters>"}}
  ],
  "suggested_fix": "<plain-English description of the fix>",
  "patch": {{
    "file": "<path>",
    "original_code": "<exact line(s) to replace>",
    "fixed_code": "<replacement code>"
  }},
  "risks": ["<risk of applying the fix>"],
  "tests_to_run": ["<test case to verify the fix>"]
}}
"""
