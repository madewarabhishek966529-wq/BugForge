import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger("bugforge.ai.provider")

class AIProvider(ABC):
    @abstractmethod
    async def analyze_bug(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the provided bug context and returns structured diagnosis and patch suggestions.
        """
        raise NotImplementedError

class MockAIProvider(AIProvider):
    async def analyze_bug(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "error_type": context.get("error_type", "TypeError"),
            "severity": "high",
            "confidence": 0.85,
            "summary": "Mock analysis: Unhandled null object access before member index.",
            "root_cause": "The target variable is None when being accessed.",
            "facts": [
                f"Exception '{context.get('error_type')}' occurred.",
                f"File location: {context.get('file_path')}:{context.get('line_number')}"
            ],
            "hypotheses": ["Function call may return None on missing key."],
            "evidence": [
                {
                    "file": context.get("file_path", "main.py"),
                    "line": context.get("line_number", 1),
                    "reason": "Exception triggered during property access."
                }
            ],
            "suggested_fix": "Add a None check before accessing properties.",
            "patch": {
                "file": context.get("file_path", "main.py"),
                "original_code": "return obj['name']",
                "fixed_code": "return obj['name'] if obj else None"
            },
            "risks": ["Callers must handle potential None return value."],
            "tests_to_run": [
                "Test function with valid dictionary.",
                "Test function with None input."
            ]
        }

def get_ai_provider(provider_name: str = None) -> AIProvider:
    name = (provider_name or settings.AI_PROVIDER).lower()
    if name == "gemini":
        from backend.app.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif name == "mock":
        return MockAIProvider()
    else:
        logger.warning(f"Unsupported provider '{name}', falling back to Mock provider.")
        return MockAIProvider()
