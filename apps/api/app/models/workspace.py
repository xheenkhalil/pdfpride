import uuid
from typing import Optional, List
from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.app.models.base import Base, TimestampMixin, GUID

class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), default="My Workspace", nullable=False)
    storage_limit_bytes: Mapped[int] = mapped_column(BigInteger, default=2147483648, nullable=False) # 2 GB
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    owner = relationship("User", back_populates="workspaces")
    folders = relationship("Folder", back_populates="workspace", cascade="all, delete-orphan")
    files = relationship("File", back_populates="workspace", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="workspace")

class Folder(Base, TimestampMixin):
    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID, ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    workspace = relationship("Workspace", back_populates="folders")
    files = relationship("File", back_populates="folder")
