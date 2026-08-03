
from uuid import UUID
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class DocumentStatus(str, Enum):
    pending = "pending"
    extracting = "extracting"
    chunking = "chunking"
    embedding = "embedding"
    ready = "ready"
    failed = "failed"


# No DocumentCreate. A document isn't created by a client POSTing a JSON body —
# it's produced server-side after a file upload (multipart/form-data, an UploadFile,
# not a Pydantic model) or after a sync job pulls content from a connector.
# Forcing a symmetrical Create schema here would misrepresent how the endpoint actually works.

class DocumentOut(BaseModel):
    id: UUID
    knowledge_source_id: UUID
    original_filename: str | None
    version: int
    status: DocumentStatus
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True
