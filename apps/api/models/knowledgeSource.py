import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, ForeignKey, Enum, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.base import Base


class KnowledgeSourceType(PyEnum):
    upload = "upload"      # Phase 1: manual file upload
    text = "text"          # Phase 1: pasted/plain text
    web = "web"             # forward — not built yet
    drive = "drive"         # forward — not built yet


class KnowledgeSourceStatus(PyEnum):
    connected = "connected"
    syncing = "syncing"
    error = "error"
    disabled = "disabled"


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[KnowledgeSourceType] = mapped_column(Enum(KnowledgeSourceType), nullable=False)
    connector_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # null for `upload`/`text` — populated for `web`/`drive` (crawl root, folder id, auth ref, etc.)

    status: Mapped[KnowledgeSourceStatus] = mapped_column(
        Enum(KnowledgeSourceStatus), nullable=False, default=KnowledgeSourceStatus.connected
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
