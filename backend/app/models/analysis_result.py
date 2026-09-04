from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey("bugs.id"), nullable=False, index=True)
    root_cause = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    suggested_fix = Column(Text, nullable=True)
    patch = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bug = relationship("Bug", back_populates="analyses")
