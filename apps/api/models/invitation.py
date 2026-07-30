# models/invitation.py
import uuid
from datetime import datetime
from sqlalchemy import Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from .enums import OrgRole, InvitationStatus

org_role_enum = PGEnum(OrgRole, name="org_role", create_type=False)
invitation_status_enum = PGEnum(InvitationStatus, name="invitation_status", create_type=False)

class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(Text, nullable=False)
    invited_role: Mapped[OrgRole] = mapped_column(org_role_enum, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(
        invitation_status_enum, nullable=False, default=InvitationStatus.PENDING
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
