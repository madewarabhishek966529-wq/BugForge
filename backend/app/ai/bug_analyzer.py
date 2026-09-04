from typing import Dict, Any, Optional
from backend.app.ai.provider import get_ai_provider, AIProvider

class AIBugAnalyzer:
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    async def analyze(self, bug_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invokes the configured AI Provider to analyze the bug context.
        """
        return await self.provider.analyze_bug(bug_data)
