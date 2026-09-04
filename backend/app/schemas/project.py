from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ProjectBase(BaseModel):
    name: str
    path: str
    language: Optional[str] = "python"

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectScanResponse(BaseModel):
    project_id: int
    files_found: int
    entry_points: List[str]
    file_map: List[str]

class ProjectRunRequest(BaseModel):
    entry_point: str
    args: Optional[List[str]] = []
