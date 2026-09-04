import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.bug import BugResponse
from backend.app.schemas.analysis import AnalysisResponse
from backend.app.services.bug_service import BugService
from backend.app.models.analysis_result import AnalysisResult
from backend.app.analyzers.context_engine import ContextEngine
from backend.app.analyzers.static.ruff_analyzer import RuffAnalyzer
from backend.app.ai.bug_analyzer import AIBugAnalyzer

logger = logging.getLogger("bugforge.api.bugs")
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

    bug.status = "Analyzing"
    db.commit()

    # ── Extract real code snippet around the error ─────────────────────────
    context_engine = ContextEngine()
    snippet_data = context_engine.extract_context(bug.file_path or "", bug.line_number or 1)

    # ── Collect static warnings from the same file ─────────────────────────
    static_warnings_text = ""
    if bug.file_path:
        try:
            ruff = RuffAnalyzer()
            file_issues = ruff.analyze(bug.file_path)
            if file_issues:
                lines = [f"  [{i['severity']}] {i['code']}: {i['message']} (line {i['line_number']})"
                         for i in file_issues[:10]]
                static_warnings_text = "\n".join(lines)
        except Exception:
            pass

    # ── Build rich context dict for AI ────────────────────────────────────
    project_name = bug.project.name if bug.project else "Unknown"
    bug_context = {
        "project_name": project_name,
        "error_type": bug.error_type,
        "message": bug.message,
        "file_path": bug.file_path,
        "line_number": bug.line_number,
        "function_name": snippet_data.get("containing_function"),
        "containing_class": snippet_data.get("containing_class"),
        "stack_trace": bug.stack_trace,
        "code_snippet": snippet_data.get("code_snippet"),
        "static_warnings": static_warnings_text or "None",
        "source": bug.source,
    }

    analyzer = AIBugAnalyzer()
    analysis_dict = await analyzer.analyze(bug_context)

    analysis_record = AnalysisResult(
        bug_id=bug.id,
        root_cause=analysis_dict.get("root_cause", "No root cause identified"),
        confidence=analysis_dict.get("confidence", 0.0),
        suggested_fix=analysis_dict.get("suggested_fix"),
        patch=analysis_dict.get("patch"),
    )
    db.add(analysis_record)

    bug.status = "Open"  # keep as Open until user applies fix
    db.commit()
    db.refresh(analysis_record)

    return analysis_record


@router.post("/bugs/{bug_id}/suggest-fix")
def suggest_fix(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    analysis = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.bug_id == bug_id)
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=400, detail="Run AI analysis first.")

    return {
        "bug_id": bug_id,
        "suggested_fix": analysis.suggested_fix,
        "patch": analysis.patch,
    }


@router.post("/bugs/{bug_id}/apply-fix")
def apply_fix(bug_id: int, db: Session = Depends(get_db)):
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    analysis = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.bug_id == bug_id)
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )
    if not analysis or not analysis.patch:
        raise HTTPException(status_code=400, detail="No patch available. Run AI analysis first.")

    import difflib
    from pathlib import Path

    patch = analysis.patch
    file_path = patch.get("file")
    original = patch.get("original_code", "")
    fixed = patch.get("fixed_code", "")

    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=400, detail=f"File not found: {file_path}")

    try:
        source = Path(file_path).read_text(encoding="utf-8")

        # Make backup
        backup_path = file_path + ".bugforge.bak"
        Path(backup_path).write_text(source, encoding="utf-8")

        # Apply patch (simple string replace)
        if original not in source:
            raise HTTPException(status_code=400, detail="Original code not found in file. Patch may be outdated.")

        patched = source.replace(original, fixed, 1)
        Path(file_path).write_text(patched, encoding="utf-8")

        bug.status = "Fixed"
        db.commit()

        diff = list(difflib.unified_diff(
            source.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=f"a/{Path(file_path).name}",
            tofile=f"b/{Path(file_path).name}",
        ))

        return {
            "message": f"Patch applied to {file_path}. Backup saved at {backup_path}.",
            "bug_id": bug_id,
            "backup": backup_path,
            "diff": "".join(diff),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply patch: {e}")
