from pydantic import BaseModel
from uuid import UUID


class UserSchema(BaseModel):
    id: UUID
    username: str
    name: str
    email: str
    created_at: str


    class Config:
        from_attributes = True
