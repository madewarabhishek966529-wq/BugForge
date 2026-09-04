from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.bug import Bug
from backend.app.schemas.bug import BugCreate

class BugService:
    @staticmethod
    def create_bug(db: Session, bug_in: BugCreate) -> Bug:
        bug = Bug(
            project_id=bug_in.project_id,
            title=bug_in.title,
            error_type=bug_in.error_type,
            message=bug_in.message,
            severity=bug_in.severity,
            file_path=bug_in.file_path,
            line_number=bug_in.line_number,
            source=bug_in.source,
            stack_trace=bug_in.stack_trace,
            status=bug_in.status
        )
        db.add(bug)
        db.commit()
        db.refresh(bug)
        return bug

    @staticmethod
    def get_bugs_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Bug]:
        return db.query(Bug).filter(Bug.project_id == project_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_bug_by_id(db: Session, bug_id: int) -> Optional[Bug]:
        return db.query(Bug).filter(Bug.id == bug_id).first()
