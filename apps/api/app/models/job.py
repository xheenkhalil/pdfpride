import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.models.base import Base, TimestampMixin, GUID

class ProcessingJob(Base, TimestampMixin):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID, ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    
    operation: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'pdf_merge', 'pdf_compress'
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True, nullable=False) # QUEUED, PROCESSING, VALIDATING, COMPLETED, FAILED
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False) # 0 to 100
    stage_message: Mapped[str] = mapped_column(String(255), default="Job queued in queue", nullable=False)
    options: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="jobs")
    workspace = relationship("Workspace", back_populates="jobs")
    job_files = relationship("JobFile", back_populates="job", cascade="all, delete-orphan")

class JobFile(Base, TimestampMixin):
    __tablename__ = "job_files"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("processing_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False) # 'input' or 'output'
    sequence_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    job = relationship("ProcessingJob", back_populates="job_files")
    file = relationship("File", back_populates="job_associations")
