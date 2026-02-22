from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    auth_provider: str = "email"
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class UserPublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    auth_provider: str
    created_at: datetime
    updated_at: datetime


class Keyword(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    text: str = Field(index=True)
    is_active: bool = Field(default=True, index=True)
    is_pinned: bool = Field(default=False, index=True)
    last_used_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class KeywordPublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    text: str
    is_active: bool
    is_pinned: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class Article(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "canonical_url"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    date_kst: str = Field(index=True)  # YYYY-MM-DD

    canonical_url: str = Field(index=True)
    original_url: str

    source_type: str = Field(index=True)  # search_api | rss
    source_name: Optional[str] = Field(default=None, index=True)

    published_at: Optional[datetime] = Field(default=None, index=True)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)

    title_original: str
    snippet_original: Optional[str] = None
    language_original: Optional[str] = Field(default=None, index=True)


class ArticleKeyword(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("article_id", "keyword_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    article_id: UUID = Field(index=True)
    keyword_id: UUID = Field(index=True)


class ProcessingResult(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("article_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    article_id: UUID = Field(index=True)

    sentiment: str = Field(index=True)  # positive | neutral | negative
    sentiment_confidence: Optional[float] = None

    summary_original: str
    summary_ko: str

    translated_from: Optional[str] = None
    translation_status: str = Field(index=True)  # not_needed | completed | failed

    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class NotificationSetting(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    daily_report_time_hhmm: str = Field(default="09:00", index=True)
    is_enabled: bool = Field(default=True, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class MemberProfile(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    status: str = Field(default="active", index=True)  # active | suspended
    points: int = Field(default=0, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class MemberAccessLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    event_type: str = Field(index=True)  # login_success | login_fail
    ip: Optional[str] = Field(default=None, index=True)
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class MemberActionLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    action_type: str = Field(index=True)  # keyword_create | keyword_update | keyword_delete | etc.
    entity_type: str = Field(index=True)
    entity_id: Optional[UUID] = Field(default=None, index=True)
    details_json: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


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


# ----- 주식 신호·알림 (PRD-stock-signal-notification) -----

class WatchItem(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "corp_code"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    corp_code: str = Field(max_length=8, index=True)  # DART 공시대상회사 고유번호 8자리
    srtn_cd: str = Field(max_length=9, index=True)  # 종목코드 6자리 (시세 API용)
    itms_nm: Optional[str] = Field(default=None, max_length=120)
    sort_order: int = Field(default=0, index=True)
    is_favorite: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class SignalRuleConfig(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    stop_loss_pct: Optional[float] = Field(default=None)  # 손절 % (예: -3.0)
    take_profit_pct: Optional[float] = Field(default=None)  # 익절 % (예: 7.0)
    ema_slope_threshold: float = Field(default=0.0)  # 25일 EMA 기울기 최소값
    volume_ratio_on: bool = Field(default=True)  # 거래량 조건 사용 여부
    volume_ratio_multiplier: float = Field(default=1.5)  # 20일 평균 대비 배수
    push_enabled: bool = Field(default=True, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class StockApiUsageLog(SQLModel, table=True):
    """시세 API 일일 호출 로그 (쿼터 가드용)."""
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    date_kst: str = Field(max_length=10, index=True)  # YYYY-MM-DD
    call_count: int = Field(default=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class PushToken(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    token: str = Field(index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class SignalEventLog(SQLModel, table=True):
    """신호 전환·푸시 발송 이력 (전량 로그)."""
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(index=True)
    corp_code: str = Field(max_length=8, index=True)
    signal_type: str = Field(index=True)  # buy | sell | hold
    reason_codes: Optional[str] = Field(default=None)  # JSON
    push_sent: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class CorpCodeCache(SQLModel, table=True):
    """DART 고유번호 목록 캐시. 하루 1회 갱신 후 검색은 DB 조회."""
    corp_code: str = Field(max_length=8, primary_key=True)
    corp_name: str = Field(max_length=200, index=True)
    stock_code: str = Field(max_length=6, index=True)  # 상장사만 저장(비어있지 않음)

