from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum


class KnowledgeSourceType(str, Enum):
    upload = "upload"
    text = "text"
    web = "web"
    drive = "drive"


class KnowledgeSourceStatus(str, Enum):
    connected = "connected"
    syncing = "syncing"
    error = "error"
    disabled = "disabled"


class KnowledgeSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: KnowledgeSourceType
    connector_config: dict | None = None

    @model_validator(mode="after")
    def validate_connector_config(self):
        # this is the app-layer check we flagged earlier — Pydantic can't express
        # "required only if type == web/drive" as a field constraint, so it goes here
        if self.type in (KnowledgeSourceType.web, KnowledgeSourceType.drive) and not self.connector_config:
            raise ValueError(f"connector_config is required for source type '{self.type.value}'")
        if self.type in (KnowledgeSourceType.upload, KnowledgeSourceType.text) and self.connector_config:
            raise ValueError(f"connector_config should not be set for source type '{self.type.value}'")
        return self


class KnowledgeSourceOut(BaseModel):
    id: UUID
    organization_id: UUID
    agent_id: UUID
    name: str
    type: KnowledgeSourceType
    status: KnowledgeSourceStatus
    last_synced_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
