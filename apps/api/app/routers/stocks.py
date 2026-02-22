"""감시종목·신호 규칙·시그널 대시보드. PRD-stock-signal-notification."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db import get_session, init_db
from ..deps import get_current_user
from ..models import SignalRuleConfig, StockApiUsageLog, User, WatchItem
from ..services import DartClient, StockPriceClient, classify_sentiment, compute_signal
from ..services.corp_search import refresh_corp_code_cache, search_from_db
from ..services.quota import today_kst
from ..services.stock_price import StockPriceRow

router = APIRouter(prefix="/stocks", tags=["stocks"])
MAX_WATCH_ITEMS = 10


# ----- schemas -----

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


# ----- 종목 검색 (종목명 → 고유번호·종목코드, DB 캐시 하루 1회 갱신) -----

@router.post("/corp-cache/refresh")
def refresh_corp_cache(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """종목 목록 수동 갱신. DART에서 고유번호 ZIP 받아 DB에 저장."""
    init_db()
    ok, count = refresh_corp_code_cache(session)
    return {"ok": ok, "count": count}


@router.get("/search", response_model=list[CorpSearchItem])
def search_corp(
    q: str = "",
    limit: int = 30,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[CorpSearchItem]:
    """종목명(회사명)으로 검색. DB 캐시 사용(하루 1회 DART에서 갱신). 상장사만 반환."""
    init_db()
    items = search_from_db(session, q, limit=min(limit, 100))
    return [CorpSearchItem(corp_code=x["corp_code"], corp_name=x["corp_name"], stock_code=x["stock_code"]) for x in items]


# ----- watchlist -----

@router.get("/watchlist", response_model=list[WatchItemPublic])
def list_watchlist(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[WatchItemPublic]:
    init_db()
    rows = session.exec(
        select(WatchItem)
        .where(WatchItem.user_id == user.id)
        .order_by(WatchItem.is_favorite.desc(), WatchItem.sort_order.asc(), WatchItem.updated_at.desc())
    ).all()
    return [
        WatchItemPublic(
            id=str(r.id),
            corp_code=r.corp_code,
            srtn_cd=r.srtn_cd,
            itms_nm=r.itms_nm,
            sort_order=r.sort_order,
            is_favorite=r.is_favorite,
            created_at=r.created_at,
        )
        for r in rows
    ]


def _norm_corp(s: str) -> str:
    return s.strip()[:8].zfill(8) if s else ""


def _norm_srtn(s: str) -> str:
    return s.strip()[:6] if s else ""


@router.post("/watchlist", response_model=WatchItemPublic, status_code=status.HTTP_201_CREATED)
def create_watch_item(
    body: WatchItemCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchItemPublic:
    init_db()
    corp = _norm_corp(body.corp_code)
    srtn = _norm_srtn(body.srtn_cd)
    if len(corp) != 8 or len(srtn) != 6:
        raise HTTPException(status_code=400, detail="corp_code 8자리, srtn_cd 6자리 필요")

    count = session.exec(select(WatchItem).where(WatchItem.user_id == user.id)).all()
    if len(count) >= MAX_WATCH_ITEMS:
        raise HTTPException(status_code=400, detail=f"감시종목은 최대 {MAX_WATCH_ITEMS}개까지")

    existing = session.exec(
        select(WatchItem).where(WatchItem.user_id == user.id, WatchItem.corp_code == corp)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 등록된 종목")

    max_order = 0
    for r in session.exec(select(WatchItem).where(WatchItem.user_id == user.id)):
        max_order = max(max_order, r.sort_order)
    item = WatchItem(
        user_id=user.id,
        corp_code=corp,
        srtn_cd=srtn,
        itms_nm=(body.itms_nm or "").strip() or None,
        sort_order=max_order + 1,
        is_favorite=False,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return WatchItemPublic(
        id=str(item.id),
        corp_code=item.corp_code,
        srtn_cd=item.srtn_cd,
        itms_nm=item.itms_nm,
        sort_order=item.sort_order,
        is_favorite=item.is_favorite,
        created_at=item.created_at,
    )


@router.delete("/watchlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watch_item(
    item_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    init_db()
    try:
        uid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid id")
    item = session.exec(
        select(WatchItem).where(WatchItem.id == uid, WatchItem.user_id == user.id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    session.delete(item)
    session.commit()


@router.patch("/watchlist/reorder", response_model=list[WatchItemPublic])
def reorder_watchlist(
    body: WatchItemReorder,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[WatchItemPublic]:
    init_db()
    ids = [x.strip() for x in body.ordered_ids if x.strip()]
    items = list(
        session.exec(select(WatchItem).where(WatchItem.user_id == user.id))
    )
    by_id = {str(r.id): r for r in items}
    for i, id_str in enumerate(ids):
        if id_str in by_id:
            by_id[id_str].sort_order = i
    for r in items:
        session.add(r)
    session.commit()
    return list_watchlist(user=user, session=session)


@router.patch("/watchlist/{item_id}/favorite", response_model=WatchItemPublic)
def toggle_favorite(
    item_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchItemPublic:
    init_db()
    try:
        uid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid id")
    item = session.exec(
        select(WatchItem).where(WatchItem.id == uid, WatchItem.user_id == user.id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    item.is_favorite = not item.is_favorite
    session.add(item)
    session.commit()
    session.refresh(item)
    return WatchItemPublic(
        id=str(item.id),
        corp_code=item.corp_code,
        srtn_cd=item.srtn_cd,
        itms_nm=item.itms_nm,
        sort_order=item.sort_order,
        is_favorite=item.is_favorite,
        created_at=item.created_at,
    )


# ----- signal rules -----

@router.get("/rules", response_model=SignalRulePublic)
def get_signal_rules(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SignalRulePublic:
    init_db()
    row = session.exec(select(SignalRuleConfig).where(SignalRuleConfig.user_id == user.id)).first()
    if not row:
        return SignalRulePublic(
            stop_loss_pct=None,
            take_profit_pct=None,
            ema_slope_threshold=0.0,
            volume_ratio_on=True,
            volume_ratio_multiplier=1.5,
            push_enabled=True,
        )
    return SignalRulePublic(
        stop_loss_pct=row.stop_loss_pct,
        take_profit_pct=row.take_profit_pct,
        ema_slope_threshold=row.ema_slope_threshold,
        volume_ratio_on=row.volume_ratio_on,
        volume_ratio_multiplier=row.volume_ratio_multiplier,
        push_enabled=row.push_enabled,
    )


@router.put("/rules", response_model=SignalRulePublic)
def update_signal_rules(
    body: SignalRuleUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SignalRulePublic:
    init_db()
    row = session.exec(select(SignalRuleConfig).where(SignalRuleConfig.user_id == user.id)).first()
    now = datetime.now().astimezone()
    if not row:
        row = SignalRuleConfig(
            user_id=user.id,
            stop_loss_pct=body.stop_loss_pct,
            take_profit_pct=body.take_profit_pct,
            ema_slope_threshold=body.ema_slope_threshold,
            volume_ratio_on=body.volume_ratio_on,
            volume_ratio_multiplier=body.volume_ratio_multiplier,
            push_enabled=body.push_enabled,
            updated_at=now,
        )
        session.add(row)
    else:
        row.stop_loss_pct = body.stop_loss_pct
        row.take_profit_pct = body.take_profit_pct
        row.ema_slope_threshold = body.ema_slope_threshold
        row.volume_ratio_on = body.volume_ratio_on
        row.volume_ratio_multiplier = body.volume_ratio_multiplier
        row.push_enabled = body.push_enabled
        row.updated_at = now
        session.add(row)
    session.commit()
    session.refresh(row)
    return SignalRulePublic(
        stop_loss_pct=row.stop_loss_pct,
        take_profit_pct=row.take_profit_pct,
        ema_slope_threshold=row.ema_slope_threshold,
        volume_ratio_on=row.volume_ratio_on,
        volume_ratio_multiplier=row.volume_ratio_multiplier,
        push_enabled=row.push_enabled,
    )


# ----- signals dashboard -----

@router.get("/signals", response_model=list[SignalItemPublic])
def get_signals(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[SignalItemPublic]:
    init_db()
    items = list(
        session.exec(
            select(WatchItem)
            .where(WatchItem.user_id == user.id)
            .order_by(WatchItem.is_favorite.desc(), WatchItem.sort_order.asc())
        )
    )
    rule = session.exec(select(SignalRuleConfig).where(SignalRuleConfig.user_id == user.id)).first()
    stop_loss = rule.stop_loss_pct if rule else None
    take_profit = rule.take_profit_pct if rule else None
    ema_th = rule.ema_slope_threshold if rule else 0.0
    vol_on = rule.volume_ratio_on if rule else True
    vol_mult = rule.volume_ratio_multiplier if rule else 1.5

    stock_client = StockPriceClient()
    dart_client = DartClient()
    date_kst = today_kst()

    # 쿼터 로그 (일일 호출 수 누적)
    usage = session.exec(
        select(StockApiUsageLog).where(StockApiUsageLog.date_kst == date_kst)
    ).first()
    if not usage:
        usage = StockApiUsageLog(date_kst=date_kst, call_count=0)
        session.add(usage)
        session.commit()
        session.refresh(usage)
    # 이번 요청에서 발생한 호출 수만큼 누적 (아래 루프에서 증가)
    base_count = usage.call_count

    result: list[SignalItemPublic] = []
    for w in items:
        last_close: int | None = None
        last_bas_dt: str | None = None
        signal = "hold"
        reasons: list[str] = ["시세 API 미설정 또는 조회 실패"]
        rows_list: list[StockPriceRow] = []

        if stock_client.is_configured():
            rows_list = stock_client.fetch(w.srtn_cd, num_days=30)
            base_count += 1
            if rows_list:
                last_close = rows_list[0].close
                last_bas_dt = getattr(rows_list[0], "bas_dt", None) or ""
                sr = compute_signal(
                    rows_list,
                    stop_loss_pct=stop_loss,
                    take_profit_pct=take_profit,
                    ema_slope_threshold=ema_th,
                    volume_ratio_on=vol_on,
                    volume_ratio_multiplier=vol_mult,
                )
                signal = sr.signal
                reasons = sr.reasons or ["조건 미충족"]
            else:
                reasons = ["시세 조회 결과 없음(종목코드·기간 확인)"]
        else:
            reasons = ["시세 API 키 미설정(.env의 STOCK_PRICE_API_KEY)"]

        disclosure_sentiment: str | None = None
        disclosure_summary: str | None = None
        if dart_client.is_configured():
            d_list = dart_client.fetch_list(w.corp_code, page_count=5)
            if d_list:
                d = d_list[0]
                disclosure_sentiment, disclosure_summary = classify_sentiment(d)

        result.append(
            SignalItemPublic(
                corp_code=w.corp_code,
                srtn_cd=w.srtn_cd,
                itms_nm=w.itms_nm,
                signal=signal,
                reasons=reasons,
                last_close=last_close,
                last_bas_dt=last_bas_dt,
                disclosure_sentiment=disclosure_sentiment,
                disclosure_summary=disclosure_summary,
            )
        )

    usage.call_count = base_count
    session.add(usage)
    session.commit()
    return result
