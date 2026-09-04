import os
import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from backend.app.core.config import settings
from backend.app.ai.provider import AIProvider
from backend.app.schemas.analysis import AIAnalysisOutput

logger = logging.getLogger("bugforge.ai.gemini")

class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = model_name or settings.AI_MODEL or "gemini-2.5-flash"

    async def analyze_bug(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY configured. Returning fallback analysis.")
            return {
                "error_type": context.get("error_type", "UnknownError"),
                "severity": "high",
                "confidence": 0.5,
                "summary": "GEMINI_API_KEY is not configured. Please set your Gemini API key in Settings or .env.",
                "root_cause": "Missing GEMINI_API_KEY configuration.",
                "facts": ["GEMINI_API_KEY environment variable or setting is empty."],
                "hypotheses": ["Configure GEMINI_API_KEY to enable AI root-cause analysis."],
                "evidence": [],
                "suggested_fix": "Add GEMINI_API_KEY to your .env file or Settings tab.",
                "patch": None,
                "risks": [],
                "tests_to_run": []
            }

        prompt = f"""
You are an expert Python debugging assistant working inside BugForge.
Analyze the following Python bug context and determine the root cause, evidence, risks, and unified patch fix.

=== BUG CONTEXT ===
Error Type: {context.get('error_type')}
Message: {context.get('message')}
File Path: {context.get('file_path')}
Line Number: {context.get('line_number')}
Function: {context.get('function_name')}

Stack Trace:
{context.get('stack_trace', 'N/A')}

Source Code Snippet (around error location):
{context.get('code_snippet', 'N/A')}

Static Analysis Findings:
{context.get('static_warnings', 'None')}
====================

Provide your diagnosis in strictly valid JSON matching this schema:
{{
  "error_type": "string",
  "severity": "critical | high | medium | low",
  "confidence": float (0.0 to 1.0),
  "summary": "string",
  "root_cause": "string",
  "facts": ["string"],
  "hypotheses": ["string"],
  "evidence": [
    {{
      "file": "string",
      "line": int,
      "reason": "string"
    }}
  ],
  "suggested_fix": "string",
  "patch": {{
    "file": "string",
    "original_code": "string",
    "fixed_code": "string"
  }},
  "risks": ["string"],
  "tests_to_run": ["string"]
}}
Return ONLY valid JSON.
"""

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            raw_text = response.text.strip()
            data = json.loads(raw_text)

            # Validate against Pydantic schema
            validated = AIAnalysisOutput(**data)
            return validated.model_dump()
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return {
                "error_type": context.get("error_type", "UnknownError"),
                "severity": "high",
                "confidence": 0.0,
                "summary": f"Gemini AI Analysis Error: {str(e)}",
                "root_cause": f"Failed to perform AI analysis: {str(e)}",
                "facts": [f"Gemini API request failed: {str(e)}"],
                "hypotheses": [],
                "evidence": [],
                "suggested_fix": "Verify API key and model availability.",
                "patch": None,
                "risks": [],
                "tests_to_run": []
            }
