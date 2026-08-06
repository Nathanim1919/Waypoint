from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    name: str
    created_at: datetime

    class Config:
        from_attributes = True