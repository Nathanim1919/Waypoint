import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.types import String, Text, Integer, DateTime
from enum import Enum as PyEnum

from app.models.base import Base


class DocumentStatus(PyEnum):
    pending = "pending"
    extracting = "extracting"
    chunking = "chunking"
    embedding = "embedding"
    ready = "ready"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False)

    original_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_storage_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    # ^ where the original uploaded file lives (S3/object storage). Confirmed.
    # extracted-text storage (inline in DB vs. separate object storage) — open, per your note. Not modeled yet.

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # sha256 of raw content — lets a re-sync detect "unchanged, skip re-processing" instead of
    # blindly re-extracting + re-embedding every time. Cheap to add now, real cost to bolt on later.

    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.pending)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
