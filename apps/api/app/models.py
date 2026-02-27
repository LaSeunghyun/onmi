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

__all__ = [
    # identity
    "User",
    "MemberProfile", "MemberAccessLog", "MemberActionLog",
    # content
    "Keyword",
    "Article", "ArticleKeyword", "ProcessingResult", "NotificationSetting",
    # stock
    "WatchItem", "SignalRuleConfig", "StockApiUsageLog",
    "PushToken", "SignalEventLog", "CorpCodeCache",
    # admin
    "AdminUser", "AdminAuditLog", "AppSetting",
    "ServiceModule", "PointAdjustmentRequest",
]
