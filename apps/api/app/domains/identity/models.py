from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    auth_provider: str = "email"
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class MemberProfile(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    status: str = Field(default="active", index=True)  # active | suspended
    points: int = Field(default=0, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class MemberAccessLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    event_type: str = Field(index=True)  # login_success | login_fail
    ip: Optional[str] = Field(default=None, index=True)
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class MemberActionLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    action_type: str = Field(index=True)  # keyword_create | keyword_update | keyword_delete | etc.
    entity_type: str = Field(index=True)
    entity_id: Optional[UUID] = Field(default=None, index=True)
    details_json: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
