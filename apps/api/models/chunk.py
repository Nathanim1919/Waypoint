
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import ForeignKey
from sqlalchemy.types import String, Text, Integer, DateTime
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import Vector


from app.models.base import Base


EMBEDDING_DIM = 1536  # placeholder — locks to whichever embedding model you pick; flag if you want to discuss

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # position within the document — needed to reconstruct order for citations,
    # and to pull in neighboring chunks as extra context at retrieval time later.

    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # page number, section heading, etc. — whatever your extractor can surface.

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
