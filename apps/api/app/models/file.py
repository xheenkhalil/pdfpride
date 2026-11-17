import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, BigInteger, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.models.base import Base, TimestampMixin, GUID

class File(Base, TimestampMixin):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True)
    
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(150), nullable=False)
    extension: Mapped[str] = mapped_column(String(20), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace = relationship("Workspace", back_populates="files")
    owner = relationship("User", back_populates="files")
    folder = relationship("Folder", back_populates="files")
    job_associations = relationship("JobFile", back_populates="file", cascade="all, delete-orphan")
