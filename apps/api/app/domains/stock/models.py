from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


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
