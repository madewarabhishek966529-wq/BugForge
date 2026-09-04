from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.project import ProjectCreate, ProjectResponse, ProjectScanResponse, ProjectRunRequest
from backend.app.schemas.bug import BugResponse, BugCreate
from backend.app.services.project_service import ProjectService
from backend.app.services.bug_service import BugService
from backend.app.analyzers.project_scanner import ProjectScanner
from backend.app.analyzers.runtime.runner import PythonRunner
from backend.app.analyzers.runtime.traceback_parser import TracebackParser

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
    
    scanner = ProjectScanner(project.path)
    try:
        scan_results = scanner.scan()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {
        "project_id": project_id,
        "files_found": scan_results["files_found"],
        "entry_points": scan_results["entry_points"],
        "file_map": scan_results["file_map"]
    }

@router.post("/{project_id}/run")
def run_project(project_id: int, request: ProjectRunRequest, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    runner = PythonRunner()
    result = runner.run_script(project.path, request.entry_point, args=request.args)

    # Parse traceback if execution produced errors
    if result["stderr"]:
        parser = TracebackParser()
        parsed_bug = parser.parse(result["stderr"])
        if parsed_bug:
            bug_in = BugCreate(
                project_id=project_id,
                title=f"{parsed_bug['error_type']}: {parsed_bug['message'] or 'Runtime Error'}",
                error_type=parsed_bug["error_type"],
                message=parsed_bug["message"],
                severity="high",
                file_path=parsed_bug["file_path"],
                line_number=parsed_bug["line_number"],
                source="runtime",
                stack_trace=parsed_bug["stack_trace"],
                status="Open"
            )
            BugService.create_bug(db, bug_in)

    return {
        "project_id": project_id,
        "entry_point": request.entry_point,
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "exit_code": result["exit_code"],
        "timed_out": result["timed_out"],
        "error": result.get("error")
    }

@router.get("/{project_id}/bugs", response_model=List[BugResponse])
def get_project_bugs(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return BugService.get_bugs_by_project(db, project_id)
