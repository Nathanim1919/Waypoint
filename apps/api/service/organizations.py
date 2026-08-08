import uuid
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
        role="owner",
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