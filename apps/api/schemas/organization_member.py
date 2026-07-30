from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from models.enums import OrgRole


class OrganizationMemberOut(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    role: OrgRole
    created_at: datetime


    class Config:
        from_attributes = True
