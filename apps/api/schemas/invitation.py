# schemas/invitation.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from models.enums import OrgRole, InvitationStatus

class InvitationCreate(BaseModel):
    email: EmailStr
    invited_role: OrgRole = OrgRole.MEMBER

class InvitationOut(BaseModel):
    id: UUID
    org_id: UUID
    email: str
    invited_role: OrgRole
    status: InvitationStatus
    created_at: datetime

    class Config:
        from_attributes = True

class InvitationAccept(BaseModel):
    """Client just hits the accept endpoint with their own auth context;
    nothing to send in the body — kept explicit in case a token/confirmation
    field is needed later."""
    pass
