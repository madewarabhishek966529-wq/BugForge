from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BugBase(BaseModel):
    title: str
    error_type: str
    message: Optional[str] = None
    severity: str = "medium"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    source: str = "static"
    stack_trace: Optional[str] = None
    status: str = "Open"

class BugCreate(BugBase):
    project_id: int

class BugResponse(BugBase):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
