from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class PatchSchema(BaseModel):
    file: str
    original_code: str
    fixed_code: str

class AIAnalysisOutput(BaseModel):
    error_type: str
    severity: str
    confidence: float
    summary: str
    root_cause: str
    facts: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_fix: str
    patch: Optional[PatchSchema] = None
    risks: List[str] = Field(default_factory=list)
    tests_to_run: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    id: int
    bug_id: int
    root_cause: str
    confidence: float
    suggested_fix: Optional[str] = None
    patch: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
