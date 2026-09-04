from abc import ABC, abstractmethod
from typing import Dict, Any

class AIProvider(ABC):
    @abstractmethod
    async def analyze_bug(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
