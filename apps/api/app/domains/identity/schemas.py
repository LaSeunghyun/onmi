from __future__ import annotations

from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from sqlmodel import SQLModel
from datetime import datetime
from uuid import UUID


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    auth_provider: str
    created_at: datetime
    updated_at: datetime
