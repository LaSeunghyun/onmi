"""감시종목·신호 규칙·시그널 대시보드. PRD-stock-signal-notification."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..db import get_session
from ..deps import get_current_user
from ..domains.identity.models import User
from ..domains.stock.schemas import (
    CorpSearchItem,
    SignalItemPublic,
    SignalRulePublic,
    SignalRuleUpdate,
    WatchItemCreate,
    WatchItemPublic,
    WatchItemReorder,
)
from ..domains.stock.service import (
    CorpSearchService,
    SignalDashboardService,
    SignalRuleService,
    WatchlistService,
)

router = APIRouter(prefix="/stocks", tags=["stocks"])


# ----- 종목 검색 -----

@router.post("/corp-cache/refresh")
def refresh_corp_cache(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """종목 목록 수동 갱신. DART에서 고유번호 ZIP 받아 DB에 저장."""
    return CorpSearchService.refresh(session)


@router.get("/search", response_model=list[CorpSearchItem])
def search_corp(
    q: str = "",
    limit: int = 30,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[CorpSearchItem]:
    """종목명(회사명)으로 검색. DB 캐시 사용(하루 1회 DART에서 갱신). 상장사만 반환."""
    return CorpSearchService.search(session, q, limit)


# ----- watchlist -----

@router.get("/watchlist", response_model=list[WatchItemPublic])
def list_watchlist(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[WatchItemPublic]:
    return WatchlistService.list_items(session, user.id)


@router.post("/watchlist", response_model=WatchItemPublic, status_code=201)
def create_watch_item(
    body: WatchItemCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchItemPublic:
    return WatchlistService.create(session, user.id, body.corp_code, body.srtn_cd, body.itms_nm)


@router.delete("/watchlist/{item_id}", status_code=204)
def delete_watch_item(
    item_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    WatchlistService.delete(session, user.id, item_id)


@router.patch("/watchlist/reorder", response_model=list[WatchItemPublic])
def reorder_watchlist(
    body: WatchItemReorder,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[WatchItemPublic]:
    return WatchlistService.reorder(session, user.id, body.ordered_ids)


@router.patch("/watchlist/{item_id}/favorite", response_model=WatchItemPublic)
def toggle_favorite(
    item_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchItemPublic:
    return WatchlistService.toggle_favorite(session, user.id, item_id)


# ----- signal rules -----

@router.get("/rules", response_model=SignalRulePublic)
def get_signal_rules(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SignalRulePublic:
    return SignalRuleService.get(session, user.id)


@router.put("/rules", response_model=SignalRulePublic)
def update_signal_rules(
    body: SignalRuleUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SignalRulePublic:
    return SignalRuleService.upsert(session, user.id, body)


# ----- signals dashboard -----

@router.get("/signals", response_model=list[SignalItemPublic])
def get_signals(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[SignalItemPublic]:
    return SignalDashboardService.compute_all(session, user.id)
