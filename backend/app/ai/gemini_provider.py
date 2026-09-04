import os
import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from backend.app.core.config import settings
from backend.app.ai.provider import AIProvider
from backend.app.ai.prompt_builder import PromptBuilder
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

        prompt = PromptBuilder().build_bug_analysis_prompt(context)

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
