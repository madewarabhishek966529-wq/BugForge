from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.project import ProjectCreate, ProjectResponse, ProjectScanResponse, ProjectRunRequest
from backend.app.schemas.bug import BugResponse
from backend.app.services.project_service import ProjectService
from backend.app.services.bug_service import BugService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(db, project_in)

@router.get("", response_model=List[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ProjectService.get_projects(db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/scan", response_model=ProjectScanResponse)
def scan_project(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project_id": project_id,
        "files_found": 0,
        "entry_points": [],
        "file_map": []
    }

@router.post("/{project_id}/analyze")
def analyze_project(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "analysis started", "project_id": project_id}

@router.post("/{project_id}/run")
def run_project(project_id: int, request: ProjectRunRequest, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "status": "completed",
        "entry_point": request.entry_point,
        "stdout": "",
        "stderr": "",
        "exit_code": 0
    }

@router.get("/{project_id}/bugs", response_model=List[BugResponse])
def get_project_bugs(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return BugService.get_bugs_by_project(db, project_id)
