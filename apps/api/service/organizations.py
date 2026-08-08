from datetime import datetime, timedelta
import uuid

from apps.api.models import invitation
from apps.api.models.enums import InvitationStatus, OrgRole
from apps.api.models.invitation import Invitation
from apps.api.models.organization import Organization
from apps.api.models.user import User
from apps.api.models.organization_member import OrganizationMember
from apps.api.schemas.organization import OrganizationCreate
from sqlalchemy.orm import Session


def create_organization(db: Session, owner_id: uuid.UUID, data: OrganizationCreate) -> Organization:
    """create_organization creates a new organization and assigns the specified user as the owner.

    Args:
        db (Session): the database session
        owner_id (UUID): the ID of the user who will own the organization
        data (OrganizationCreate): the data for creating the organization

    Returns:
        Organization: the created organization
    """
    
    organization = Organization(
        name=data.name,
    )
    
    db.add(organization)
    db.flush()  # Flush to get the organization ID before committing
    
    organization_member = OrganizationMember(
        org_id=organization.id,
        user_id=owner_id,
        role=OrgRole.OWNER,
    )
    
    db.add(organization_member)
    
    db.commit()
    db.refresh(organization)
    return organization


def get_organization_by_id(db: Session, org_id: uuid.UUID, user_id: uuid.UUID) -> Organization | None:
    """
get_organization_by_id retrieves an organization by its ID, ensuring that the requesting user is a member of that organization.

    Args:
        db (Session): the database session
        org_id (UUID): the ID of the organization to retrieve
        user_id (UUID): the ID of the user requesting the organization

    Returns:
        Organization | None: the retrieved organization or None if not found
    """
    return (
        db.query(Organization)
           .join(OrganizationMember, Organization.id == OrganizationMember.org_id)
           .filter(Organization.id == org_id, OrganizationMember.user_id == user_id)
           .first()
        )
        


def list_organizations_by_user(db: Session, user_id: uuid.UUID) -> list[Organization]:
    """list_organizations_by_user retrieves all organizations that a user is a member of.

    Args:
        db (Session): the database session
        user_id (UUID): the ID of the user whose organizations to list

    Returns:
        list[Organization]: a list of organizations the user is a member of
    """
    return (
        db.query(Organization)
        .join(OrganizationMember, Organization.id == OrganizationMember.org_id)
        .filter(OrganizationMember.user_id == user_id)
        .all()
    )
    
def get_organization_members(db:Session, org_id: uuid.UUID) -> list[OrganizationMember]:
    """
    get_organization_members retrieves all members of a specific organization.

    Args:
        db (Session): the database session
        org_id (UUID): the ID of the organization
    Returns:
        list[OrganizationMember]: the retrieved organization members
    """
    return (db.query(OrganizationMember)
            .join(Organization, Organization.id == OrganizationMember.org_id)
            .filter(OrganizationMember.org_id == org_id))
    
    
def invite_member(db: Session, org_id:uuid.UUID, email: str, role: OrgRole, created_by: uuid.UUID) -> Invitation:
    """Creates a pending Invitation for the given email. Does not create an
        OrganizationMember — that only happens when the invite is accepted.

    Args:
        db (Session): the database session
        org_id (UUID): the ID of the organization
        email (str): the email of the user to invite
        role (OrgRole): the role to assign to the new member
        created_by (UUID): the ID of the user sending the invite

    Returns:
        Invitation: the created invitation
    """
    # send email with invite link to user with email and insert into invites table with org_id, email, role, and a unique token
    
    # create Invitation entry in the database
    invitation = Invitation(
        org_id=org_id,
        email=email,
        invited_role=role,
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=15),  # Set expiration date
        created_by=created_by,
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # send email with invite link to user with email and insert into invites table with org_id, email, role, and a unique token
    invite_token = str(invitation.id)    # Here you would send the email with the invite_token to the user's email address.
    send_email(email, invite_token)
    
    
    
    
def accept_invitation(db: Session, invite_id: str) -> OrganizationMember:
    """Accepts an invitation and creates an OrganizationMember entry.

    Args:
        db (Session): the database session
        invite_token (str): the token for the invitation
        user_id (UUID): the ID of the user accepting the invitation

    Returns:
        OrganizationMember: the created organization member
    """
    
    invitation = db.query(Invitation).filter(Invitation.id == invite_id).first()
    if not invitation:
        raise ValueError("Invalid invitation token")
    
    if invitation.status != InvitationStatus.PENDING:
        raise ValueError("Invitation has already been accepted or is no longer valid")
    
    # look up the user by email
    user = db.query(User).filter(User.email == invitation.email).first()
    if not user:
        raise ValueError("No user found with the provided email")
    
    # create OrganizationMember entry
    organization_member = OrganizationMember(
        org_id=invitation.org_id,
        user_id=user.id,
        role=invitation.invited_role,
    )
    db.add(organization_member)
    db.commit()
    db.refresh(organization_member)