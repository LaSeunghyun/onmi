from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import SQLModel


class KeywordPublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    text: str
    is_active: bool
    is_pinned: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class KeywordCreate(SQLModel):
    text: str
    is_active: bool = True


class KeywordUpdate(SQLModel):
    is_active: Optional[bool] = None
    is_pinned: Optional[bool] = None
