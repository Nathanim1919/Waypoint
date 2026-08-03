
from uuid import UUID
from pydantic import BaseModel


class ChunkCitation(BaseModel):
    """What gets attached to a chat response as a source — not a general-purpose ChunkOut."""
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int

    class Config:
        from_attributes = True
