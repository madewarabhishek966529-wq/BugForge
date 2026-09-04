from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.bug import BugResponse
from backend.app.schemas.analysis import AnalysisResponse
from backend.app.services.bug_service import BugService

router = APIRouter(tags=["bugs"])

@router.get("/bugs/{bug_id}", response_model=BugResponse)
def get_bug(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug

@router.post("/bugs/{bug_id}/ai-analyze")
def ai_analyze_bug(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return {"message": "AI analysis stub", "bug_id": bug_id}

@router.post("/bugs/{bug_id}/suggest-fix")
def suggest_fix(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return {"message": "Suggest fix stub", "bug_id": bug_id}

@router.post("/bugs/{bug_id}/apply-fix")
def apply_fix(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return {"message": "Apply fix stub", "bug_id": bug_id}
