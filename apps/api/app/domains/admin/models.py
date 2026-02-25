from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class AdminUser(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("admin_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    admin_id: str = Field(index=True)
    password_hash: str
    role: str = Field(default="super_admin", index=True)
    must_change_password: bool = Field(default=True, index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class ServiceModule(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("module_key"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    module_key: str = Field(index=True)
    name: str
    route_path: str
    description: Optional[str] = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class AdminAuditLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    admin_user_id: UUID = Field(index=True)
    action_type: str = Field(index=True)
    target_type: str = Field(index=True)
    target_id: Optional[UUID] = Field(default=None, index=True)
    reason: Optional[str] = None
    before_json: Optional[str] = None
    after_json: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class AppSetting(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("key"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    key: str = Field(index=True)
    value: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class PointAdjustmentRequest(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    member_user_id: UUID = Field(index=True)
    amount: int
    reason: str
    requested_by_admin_id: UUID = Field(index=True)
    approved_by_admin_id: Optional[UUID] = Field(default=None, index=True)
    status: str = Field(default="requested", index=True)  # requested | approved | rejected | applied
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
