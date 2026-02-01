"""User schemas."""

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True
