"""공공데이터포털 금융위원회_주식시세정보 getStockPriceInfo 연동.
일일 트래픽 10,000건, 30 TPS. 데이터 갱신주기 일 1회."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from urllib.parse import unquote

import httpx

from ..settings import settings

BASE_URL = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"


def _parse_item(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "bas_dt": raw.get("basDt"),
        "srtn_cd": raw.get("srtnCd"),
        "itms_nm": raw.get("itmsNm"),
        "clpr": _int(raw.get("clpr")),
        "mkp": _int(raw.get("mkp")),
        "hipr": _int(raw.get("hipr")),
        "lopr": _int(raw.get("lopr")),
        "trqu": _int(raw.get("trqu")),
        "vs": _int(raw.get("vs")),
        "flt_rt": _float(raw.get("fltRt")),
    }


def _int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class StockPriceRow:
    def __init__(self, data: dict[str, Any]) -> None:
        self.bas_dt = data.get("bas_dt") or ""
        self.srtn_cd = data.get("srtn_cd") or ""
        self.itms_nm = data.get("itms_nm") or ""
        self.clpr = data.get("clpr")
        self.mkp = data.get("mkp")
        self.hipr = data.get("hipr")
        self.lopr = data.get("lopr")
        self.trqu = data.get("trqu")
        self.vs = data.get("vs")
        self.flt_rt = data.get("flt_rt")

    @property
    def close(self) -> int | None:
        return self.clpr

    @property
    def volume(self) -> int | None:
        return self.trqu


class StockPriceClient:
    def __init__(self, api_key: str | None = None) -> None:
        raw = (api_key or settings.stock_price_api_key or "").strip()
        self.api_key = unquote(raw) if raw else ""

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def fetch(
        self,
        srtn_cd: str,
        *,
        end_dt: datetime | None = None,
        num_days: int = 30,
    ) -> list[StockPriceRow]:
        """종목코드(srtn_cd 6자리) 기준 최근 일별 시세 조회. 최대 num_days건."""
        if not self.api_key:
            return []
        end = end_dt or datetime.now()
        end_str = end.strftime("%Y%m%d")
        begin = end - timedelta(days=num_days + 10)
        begin_str = begin.strftime("%Y%m%d")

        params: dict[str, str | int] = {
            "serviceKey": self.api_key,
            "numOfRows": min(num_days, 100),
            "pageNo": 1,
            "resultType": "json",
            "likeSrtnCd": srtn_cd.strip(),
            "beginBasDt": begin_str,
            "endBasDt": end_str,
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                r = client.get(BASE_URL, params=params)
                r.raise_for_status()
        except Exception:
            return []

        data = r.json()
        res = data.get("response") or data
        header = (res.get("header") or {}) or {}
        if header.get("resultCode") != "00":
            return []

        body = res.get("body") or {}
        raw_items = body.get("items")
        if raw_items is None:
            raw_items = []
        # 공공데이터 JSON: items.item (단일 객체) 또는 items.item (배열) 또는 items가 배열
        if isinstance(raw_items, dict):
            item = raw_items.get("item")
            if item is None:
                items = [raw_items]
            elif isinstance(item, list):
                items = item
            else:
                items = [item]
        else:
            items = raw_items if isinstance(raw_items, list) else []
        rows = [_parse_item(it) for it in items]
        # 최신일 순 정렬 후 상위 num_days건
        rows.sort(key=lambda x: x.get("bas_dt") or "", reverse=True)
        return [StockPriceRow(r) for r in rows[:num_days]]
