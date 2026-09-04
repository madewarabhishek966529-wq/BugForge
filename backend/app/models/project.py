from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    path = Column(String, nullable=False)
    language = Column(String, default="python")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bugs = relationship("Bug", back_populates="project", cascade="all, delete-orphan")
