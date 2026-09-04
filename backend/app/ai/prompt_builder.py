from typing import Dict, Any

class PromptBuilder:
    def build_bug_analysis_prompt(self, context: Dict[str, Any]) -> str:
        return f"Analyze the following bug context: {context}"
