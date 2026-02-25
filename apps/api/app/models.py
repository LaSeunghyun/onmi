"""하위 호환 re-export. 새 코드는 domains/*/models.py를 직접 import하세요."""
from __future__ import annotations

from .domains.admin.models import (
    AdminAuditLog,
    AdminUser,
    AppSetting,
    PointAdjustmentRequest,
    ServiceModule,
)
from .domains.content.models import (
    Article,
    ArticleKeyword,
    Keyword,
    NotificationSetting,
    ProcessingResult,
)
from .domains.identity.models import (
    MemberAccessLog,
    MemberActionLog,
    MemberProfile,
    User,
)
from .domains.stock.models import (
    CorpCodeCache,
    PushToken,
    SignalEventLog,
    SignalRuleConfig,
    StockApiUsageLog,
    WatchItem,
)

# 하위 호환 DTO (이전 위치에서 정의했던 것)
from pydantic import ConfigDict
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserPublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    auth_provider: str
    created_at: datetime
    updated_at: datetime


class KeywordPublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    text: str
    is_active: bool
    is_pinned: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


__all__ = [
    # identity
    "User", "UserPublic",
    "MemberProfile", "MemberAccessLog", "MemberActionLog",
    # content
    "Keyword", "KeywordPublic",
    "Article", "ArticleKeyword", "ProcessingResult", "NotificationSetting",
    # stock
    "WatchItem", "SignalRuleConfig", "StockApiUsageLog",
    "PushToken", "SignalEventLog", "CorpCodeCache",
    # admin
    "AdminUser", "AdminAuditLog", "AppSetting",
    "ServiceModule", "PointAdjustmentRequest",
]
