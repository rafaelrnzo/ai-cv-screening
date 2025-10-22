from sqlalchemy import Column, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class JobResult(Base):
    __tablename__ = "job_results"

    id = Column(String, primary_key=True, index=True)
    job_title = Column(String)
    cv_id = Column(String)
    report_id = Column(String)
    cv_match_rate = Column(Float, nullable=True)
    cv_feedback = Column(Text, nullable=True)
    project_score = Column(Float, nullable=True)
    project_feedback = Column(Text, nullable=True)
    overall_summary = Column(Text, nullable=True)
    status = Column(String, default="queued")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
