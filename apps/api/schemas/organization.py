# schemas/organization.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    created_at: datetime


    class Config:
        from_attributes = True
