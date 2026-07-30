# models/enums.py
import enum

class OrgRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"

class AgentAccessLevel(str, enum.Enum):
    VIEWER = "VIEWER"
    USER = "USER"
