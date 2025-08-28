import uuid
from typing import Optional

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import Field, EmailStr


class User(BaseUser):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(BaseUserCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
