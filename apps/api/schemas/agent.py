from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime



class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    instruction: str = Field(min_length=1)
    model: str


class AgentOut(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    description: str | None
    instruction: str
    model: str
    created_at: datetime


    class Config:
        from_attributes = True
