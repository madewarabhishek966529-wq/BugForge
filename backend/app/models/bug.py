from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    error_type = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    severity = Column(String, default="medium")  # critical, high, medium, low
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    source = Column(String, default="static")  # static, runtime, ast
    stack_trace = Column(Text, nullable=True)
    status = Column(String, default="Open")  # Open, Analyzing, Fixed, Ignored
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="bugs")
    analyses = relationship("AnalysisResult", back_populates="bug", cascade="all, delete-orphan")
