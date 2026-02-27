"""주식 감시종목·신호 규칙·대시보드 Application Service."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from ...external.corp_search import refresh_corp_code_cache, search_from_db
from ...external.dart import DartClient
from ...external.disclosure import classify_sentiment
from ...external.stock_price import StockPriceClient
from ...settings import settings
from .models import SignalRuleConfig, StockApiUsageLog, WatchItem
from .schemas import (
    CorpSearchItem,
    SignalItemPublic,
    SignalRulePublic,
    WatchItemPublic,
)
from .signal import compute_signal


def _today_kst() -> str:
    from datetime import timezone, timedelta
    KST = timezone(timedelta(hours=9))
    return datetime.now(KST).strftime("%Y-%m-%d")


def _norm_corp(s: str) -> str:
    return s.strip()[:8].zfill(8) if s else ""


def _norm_srtn(s: str) -> str:
    return s.strip()[:6] if s else ""


def _watch_to_public(item: WatchItem) -> WatchItemPublic:
    return WatchItemPublic(
        id=str(item.id),
        corp_code=item.corp_code,
        srtn_cd=item.srtn_cd,
        itms_nm=item.itms_nm,
        sort_order=item.sort_order,
        is_favorite=item.is_favorite,
        created_at=item.created_at,
    )


class CorpSearchService:
    @staticmethod
    def refresh(session: Session) -> dict:
        ok, count = refresh_corp_code_cache(session)
        return {"ok": ok, "count": count}

    @staticmethod
    def search(session: Session, query: str, limit: int) -> list[CorpSearchItem]:
        items = search_from_db(session, query, limit=min(limit, 100))
        return [CorpSearchItem(corp_code=x["corp_code"], corp_name=x["corp_name"], stock_code=x["stock_code"]) for x in items]


class WatchlistService:
    @staticmethod
    def list_items(session: Session, user_id: UUID) -> list[WatchItemPublic]:
        rows = session.exec(
            select(WatchItem)
            .where(WatchItem.user_id == user_id)
            .order_by(WatchItem.is_favorite.desc(), WatchItem.sort_order.asc(), WatchItem.updated_at.desc())
        ).all()
        return [_watch_to_public(r) for r in rows]

    @staticmethod
    def create(session: Session, user_id: UUID, corp_code: str, srtn_cd: str, itms_nm: str | None) -> WatchItemPublic:
        corp = _norm_corp(corp_code)
        srtn = _norm_srtn(srtn_cd)
        if len(corp) != 8 or len(srtn) != 6:
            raise HTTPException(status_code=400, detail="corp_code 8자리, srtn_cd 6자리 필요")

        count = session.exec(
            select(func.count(WatchItem.id)).where(WatchItem.user_id == user_id)
        ).one()
        if count >= settings.max_watch_items:
            raise HTTPException(status_code=400, detail=f"감시종목은 최대 {settings.max_watch_items}개까지")

        existing = session.exec(
            select(WatchItem).where(WatchItem.user_id == user_id, WatchItem.corp_code == corp)
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="이미 등록된 종목")

        max_order = session.exec(
            select(func.coalesce(func.max(WatchItem.sort_order), 0))
            .where(WatchItem.user_id == user_id)
        ).one()

        item = WatchItem(
            user_id=user_id,
            corp_code=corp,
            srtn_cd=srtn,
            itms_nm=(itms_nm or "").strip() or None,
            sort_order=max_order + 1,
            is_favorite=False,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return _watch_to_public(item)

    @staticmethod
    def delete(session: Session, user_id: UUID, item_id: str) -> None:
        try:
            uid = UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid id")
        item = session.exec(
            select(WatchItem).where(WatchItem.id == uid, WatchItem.user_id == user_id)
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="not found")
        session.delete(item)
        session.commit()

    @staticmethod
    def reorder(session: Session, user_id: UUID, ordered_ids: list[str]) -> list[WatchItemPublic]:
        ids = [x.strip() for x in ordered_ids if x.strip()]
        items = list(session.exec(select(WatchItem).where(WatchItem.user_id == user_id)))
        by_id = {str(r.id): r for r in items}
        for i, id_str in enumerate(ids):
            if id_str in by_id:
                by_id[id_str].sort_order = i
        for r in items:
            session.add(r)
        session.commit()
        return WatchlistService.list_items(session, user_id)

    @staticmethod
    def toggle_favorite(session: Session, user_id: UUID, item_id: str) -> WatchItemPublic:
        try:
            uid = UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid id")
        item = session.exec(
            select(WatchItem).where(WatchItem.id == uid, WatchItem.user_id == user_id)
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="not found")
        item.is_favorite = not item.is_favorite
        session.add(item)
        session.commit()
        session.refresh(item)
        return _watch_to_public(item)


class SignalRuleService:
    @staticmethod
    def get(session: Session, user_id: UUID) -> SignalRulePublic:
        row = session.exec(select(SignalRuleConfig).where(SignalRuleConfig.user_id == user_id)).first()
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

    @staticmethod
    def upsert(session: Session, user_id: UUID, data: "SignalRuleUpdate") -> SignalRulePublic:
        from .schemas import SignalRuleUpdate
        row = session.exec(select(SignalRuleConfig).where(SignalRuleConfig.user_id == user_id)).first()
        now = datetime.now().astimezone()
        if not row:
            row = SignalRuleConfig(
                user_id=user_id,
                stop_loss_pct=data.stop_loss_pct,
                take_profit_pct=data.take_profit_pct,
                ema_slope_threshold=data.ema_slope_threshold,
                volume_ratio_on=data.volume_ratio_on,
                volume_ratio_multiplier=data.volume_ratio_multiplier,
                push_enabled=data.push_enabled,
                updated_at=now,
            )
            session.add(row)
        else:
            row.stop_loss_pct = data.stop_loss_pct
            row.take_profit_pct = data.take_profit_pct
            row.ema_slope_threshold = data.ema_slope_threshold
            row.volume_ratio_on = data.volume_ratio_on
            row.volume_ratio_multiplier = data.volume_ratio_multiplier
            row.push_enabled = data.push_enabled
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


class SignalDashboardService:
    @staticmethod
    def _fetch_stock_data(
        stock_client: StockPriceClient,
        dart_client: DartClient,
        srtn_cd: str,
        corp_code: str,
    ) -> dict[str, Any]:
        """외부 API 호출 (스레드 풀에서 병렬 실행)."""
        rows_list = stock_client.fetch(srtn_cd, num_days=50) if stock_client.is_configured() else []
        d_list = dart_client.fetch_list(corp_code, page_count=5) if dart_client.is_configured() else []
        return {"rows_list": rows_list, "d_list": d_list}

    @staticmethod
    def compute_all(session: Session, user_id: UUID) -> list[SignalItemPublic]:
        items = list(
            session.exec(
                select(WatchItem)
                .where(WatchItem.user_id == user_id)
                .order_by(WatchItem.is_favorite.desc(), WatchItem.sort_order.asc())
            )
        )
        rule = session.exec(select(SignalRuleConfig).where(SignalRuleConfig.user_id == user_id)).first()
        stop_loss = rule.stop_loss_pct if rule else None
        take_profit = rule.take_profit_pct if rule else None
        ema_th = rule.ema_slope_threshold if rule else 0.0
        vol_on = rule.volume_ratio_on if rule else True
        vol_mult = rule.volume_ratio_multiplier if rule else 1.5

        stock_client = StockPriceClient()
        dart_client = DartClient()
        date_kst = _today_kst()

        usage = session.exec(
            select(StockApiUsageLog).where(StockApiUsageLog.date_kst == date_kst)
        ).first()
        if not usage:
            usage = StockApiUsageLog(date_kst=date_kst, call_count=0)
            session.add(usage)
            session.commit()
            session.refresh(usage)

        # 외부 API 호출을 스레드 풀에서 병렬 실행
        fetched: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=min(len(items), 5)) as pool:
            futures = {
                pool.submit(
                    SignalDashboardService._fetch_stock_data,
                    stock_client, dart_client, w.srtn_cd, w.corp_code,
                ): w.corp_code
                for w in items
            }
            for future in as_completed(futures):
                corp_code = futures[future]
                try:
                    fetched[corp_code] = future.result()
                except Exception:
                    fetched[corp_code] = {"rows_list": [], "d_list": []}

        api_call_count = sum(1 for w in items if stock_client.is_configured())

        result: list[SignalItemPublic] = []
        for w in items:
            data = fetched.get(w.corp_code, {"rows_list": [], "d_list": []})
            rows_list = data["rows_list"]
            d_list = data["d_list"]

            last_close: int | None = None
            last_bas_dt: str | None = None
            signal = "hold"
            reasons: list[str] = ["시세 API 미설정 또는 조회 실패"]

            if stock_client.is_configured():
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
            if d_list:
                disclosure_sentiment, disclosure_summary = classify_sentiment(d_list[0])

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

        usage.call_count = usage.call_count + api_call_count
        session.add(usage)
        session.commit()
        return result
