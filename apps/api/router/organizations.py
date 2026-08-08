# Organization Router

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from apps.api.dependencies.auth import get_current_user
from apps.api.dependencies.db import get_db
from apps.api.models.user import User
from apps.api.schemas.organization import OrganizationCreate, OrganizationOut
from apps.api.service.organizations import create_organization as create_org, get_organization_by_id as get_org_by_id, list_organizations_by_user as list_orgs_by_user



router = APIRouter(
    prefix="/organizations",
    tags=["organizations"]
)

@router.post("/", response_model=OrganizationOut, status_code=201)
def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    organization = create_org(db, current_user.id, data)
    return organization


@router.get("/{org_id}", response_model=OrganizationOut, status_code=200)
def get_organization(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    organization = get_org_by_id(db, org_id, current_user.id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found or access denied")
    return organization



@router.get("/", response_model=list[OrganizationOut], status_code=200)
def list_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    organizations = list_orgs_by_user(db, current_user.id)
    return organizations
