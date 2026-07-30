# models/agent_member.py
import uuid
from datetime import datetime
from sqlalchemy import TIMESTAMP, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from .enums import AgentAccessLevel

agent_access_level_enum = PGEnum(AgentAccessLevel, name="agent_access_level", create_type=False)

class AgentMember(Base):
    __tablename__ = "agent_members"
    __table_args__ = (UniqueConstraint("agent_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_level: Mapped[AgentAccessLevel] = mapped_column(agent_access_level_enum, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
