import logging
from typing import List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.project import ProjectCreate, ProjectResponse, ProjectScanResponse, ProjectRunRequest
from backend.app.schemas.bug import BugResponse, BugCreate
from backend.app.services.project_service import ProjectService
from backend.app.services.bug_service import BugService
from backend.app.analyzers.project_scanner import ProjectScanner
from backend.app.analyzers.static.ruff_analyzer import RuffAnalyzer
from backend.app.analyzers.static.pylint_analyzer import PylintAnalyzer
from backend.app.analyzers.static.ast_analyzer import ASTAnalyzer
from backend.app.analyzers.runtime.runner import PythonRunner
from backend.app.analyzers.runtime.traceback_parser import TracebackParser

logger = logging.getLogger("bugforge.api.projects")
router = APIRouter(prefix="/projects", tags=["projects"])


# ── CRUD ───────────────────────────────────────────────────────────────────────

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


# ── SCAN (Ruff + Pylint + AST → store bugs) ────────────────────────────────────

@router.post("/{project_id}/scan")
def scan_project(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scanner = ProjectScanner(project.path)
    try:
        scan_results = scanner.scan()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    all_issues: List[Dict[str, Any]] = []

    # ── Ruff ──────────────────────────────────────────────────────────────────
    try:
        ruff_issues = RuffAnalyzer().analyze(project.path)
        logger.info(f"Ruff found {len(ruff_issues)} issues in project {project_id}")
        all_issues.extend(ruff_issues)
    except Exception as e:
        logger.error(f"Ruff analysis failed: {e}")

    # ── Pylint ────────────────────────────────────────────────────────────────
    try:
        pylint_issues = PylintAnalyzer().analyze(project.path)
        logger.info(f"Pylint found {len(pylint_issues)} issues in project {project_id}")
        all_issues.extend(pylint_issues)
    except Exception as e:
        logger.error(f"Pylint analysis failed: {e}")

    # ── AST (per file) ────────────────────────────────────────────────────────
    ast_analyzer = ASTAnalyzer()
    for rel_path in scan_results["file_map"]:
        full_path = str(Path(project.path) / rel_path)
        try:
            ast_issues = ast_analyzer.analyze(full_path)
            logger.info(f"AST found {len(ast_issues)} issues in {rel_path}")
            all_issues.extend(ast_issues)
        except Exception as e:
            logger.error(f"AST analysis failed for {rel_path}: {e}")

    # ── Deduplicate (same file + line + code) ─────────────────────────────────
    seen: set = set()
    unique_issues: List[Dict[str, Any]] = []
    for issue in all_issues:
        key = (issue.get("file_path"), issue.get("line_number"), issue.get("code"))
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    # ── Store bugs in DB ──────────────────────────────────────────────────────
    stored = 0
    for issue in unique_issues:
        try:
            bug_in = BugCreate(
                project_id=project_id,
                title=f"{issue['error_type']}: {issue['message'][:120]}",
                error_type=issue["error_type"],
                message=issue["message"],
                severity=issue.get("severity", "medium"),
                file_path=issue.get("file_path"),
                line_number=issue.get("line_number"),
                source=issue.get("source", "static"),
                stack_trace=None,
                status="Open",
            )
            BugService.create_bug(db, bug_in)
            stored += 1
        except Exception as e:
            logger.error(f"Failed to store bug: {e}")

    return {
        "project_id": project_id,
        "files_found": scan_results["files_found"],
        "entry_points": scan_results["entry_points"],
        "file_map": scan_results["file_map"],
        "bugs_found": len(unique_issues),
        "bugs_stored": stored,
        "summary": {
            "ruff": len([i for i in unique_issues if i.get("tool") == "ruff"]),
            "pylint": len([i for i in unique_issues if i.get("tool") == "pylint"]),
            "ast": len([i for i in unique_issues if i.get("tool") == "ast"]),
        },
    }


# ── ANALYZE (alias for scan — static only) ────────────────────────────────────

@router.post("/{project_id}/analyze")
def analyze_project(project_id: int, db: Session = Depends(get_db)):
    return scan_project(project_id, db)


# ── RUN (subprocess + traceback → store runtime bugs) ─────────────────────────

@router.post("/{project_id}/run")
def run_project(project_id: int, request: ProjectRunRequest, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    runner = PythonRunner()
    result = runner.run_script(project.path, request.entry_point, args=request.args)

    bug_created = None
    if result["stderr"]:
        parser = TracebackParser()
        parsed_bug = parser.parse(result["stderr"])
        if parsed_bug:
            try:
                bug_in = BugCreate(
                    project_id=project_id,
                    title=f"{parsed_bug['error_type']}: {(parsed_bug['message'] or 'Runtime Error')[:120]}",
                    error_type=parsed_bug["error_type"],
                    message=parsed_bug["message"],
                    severity="high",
                    file_path=parsed_bug["file_path"],
                    line_number=parsed_bug["line_number"],
                    source="runtime",
                    stack_trace=parsed_bug["stack_trace"],
                    status="Open",
                )
                bug = BugService.create_bug(db, bug_in)
                bug_created = bug.id
            except Exception as e:
                logger.error(f"Failed to store runtime bug: {e}")

    return {
        "project_id": project_id,
        "entry_point": request.entry_point,
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "exit_code": result["exit_code"],
        "timed_out": result["timed_out"],
        "error": result.get("error"),
        "bug_id": bug_created,
    }


# ── BUGS list ─────────────────────────────────────────────────────────────────

@router.get("/{project_id}/bugs", response_model=List[BugResponse])
def get_project_bugs(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return BugService.get_bugs_by_project(db, project_id)
