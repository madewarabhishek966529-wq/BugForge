from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.bug import BugResponse
from backend.app.schemas.analysis import AnalysisResponse
from backend.app.services.bug_service import BugService
from backend.app.models.analysis_result import AnalysisResult
from backend.app.analyzers.context_engine import ContextEngine
from backend.app.ai.bug_analyzer import AIBugAnalyzer

router = APIRouter(tags=["bugs"])

@router.get("/bugs/{bug_id}", response_model=BugResponse)
def get_bug(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug

@router.post("/bugs/{bug_id}/ai-analyze", response_model=AnalysisResponse)
async def ai_analyze_bug(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    # Update bug status to 'Analyzing'
    bug.status = "Analyzing"
    db.commit()

    # Extract relevant context snippet
    context_engine = ContextEngine()
    snippet_data = context_engine.extract_context(bug.file_path or "", bug.line_number or 1)

    bug_context = {
        "error_type": bug.error_type,
        "message": bug.message,
        "file_path": bug.file_path,
        "line_number": bug.line_number,
        "stack_trace": bug.stack_trace,
        "code_snippet": snippet_data.get("code_snippet"),
        "function_name": snippet_data.get("containing_function")
    }

    analyzer = AIBugAnalyzer()
    analysis_dict = await analyzer.analyze(bug_context)

    # Store analysis result in DB
    analysis_record = AnalysisResult(
        bug_id=bug.id,
        root_cause=analysis_dict.get("root_cause", "No root cause identified"),
        confidence=analysis_dict.get("confidence", 0.0),
        suggested_fix=analysis_dict.get("suggested_fix"),
        patch=analysis_dict.get("patch")
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    return analysis_record

@router.post("/bugs/{bug_id}/suggest-fix")
def suggest_fix(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    # Fetch latest analysis
    analysis = db.query(AnalysisResult).filter(AnalysisResult.bug_id == bug_id).order_by(AnalysisResult.created_at.desc()).first()
    if not analysis:
        raise HTTPException(status_code=400, detail="No AI analysis found for this bug. Run AI analysis first.")

    return {
        "bug_id": bug_id,
        "suggested_fix": analysis.suggested_fix,
        "patch": analysis.patch
    }

@router.post("/bugs/{bug_id}/apply-fix")
def apply_fix(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    bug.status = "Fixed"
    db.commit()
    return {"message": f"Bug #{bug_id} status updated to Fixed.", "bug_id": bug_id}
