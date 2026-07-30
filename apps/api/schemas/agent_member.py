# schemas/agent_member.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from models.enums import AgentAccessLevel

class AgentMemberCreate(BaseModel):
    user_id: UUID
    access_level: AgentAccessLevel = AgentAccessLevel.USER

class AgentMemberOut(BaseModel):
    id: UUID
    agent_id: UUID
    user_id: UUID
    access_level: AgentAccessLevel
    created_at: datetime

    class Config:
        from_attributes = True
