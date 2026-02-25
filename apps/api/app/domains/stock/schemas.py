from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WatchItemCreate(BaseModel):
    corp_code: str
    srtn_cd: str
    itms_nm: str | None = None


class WatchItemPublic(BaseModel):
    id: str
    corp_code: str
    srtn_cd: str
    itms_nm: str | None
    sort_order: int
    is_favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WatchItemReorder(BaseModel):
    ordered_ids: list[str]  # UUID 문자열 순서


class SignalRuleUpdate(BaseModel):
    stop_loss_pct: float | None = None
    take_profit_pct: float | None = None
    ema_slope_threshold: float = 0.0
    volume_ratio_on: bool = True
    volume_ratio_multiplier: float = 1.5
    push_enabled: bool = True


class SignalRulePublic(BaseModel):
    stop_loss_pct: float | None
    take_profit_pct: float | None
    ema_slope_threshold: float
    volume_ratio_on: bool
    volume_ratio_multiplier: float
    push_enabled: bool


class SignalItemPublic(BaseModel):
    corp_code: str
    srtn_cd: str
    itms_nm: str | None
    signal: str  # buy | sell | hold
    reasons: list[str]
    last_close: int | None
    last_bas_dt: str | None
    disclosure_sentiment: str | None  # positive | neutral | negative
    disclosure_summary: str | None


class CorpSearchItem(BaseModel):
    corp_code: str
    corp_name: str
    stock_code: str  # 6자리 srtn_cd
