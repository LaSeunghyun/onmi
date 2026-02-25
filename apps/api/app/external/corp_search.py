"""DART 고유번호 목록: 하루 1회 ZIP 다운로드 후 DB 저장. 검색은 DB 조회."""
from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlmodel import Session, col, delete, select

from ..domains.admin.models import AppSetting
from ..domains.stock.models import CorpCodeCache
from ..settings import settings

CORPCODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"
CACHE_DATE_KEY = "corp_code_last_fetched_date"

KST = timezone(timedelta(hours=9))


def _today_kst() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def _fetch_zip() -> bytes | None:
    key = (settings.dart_api_key or "").strip()
    if not key:
        return None
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(CORPCODE_URL, params={"crtfc_key": key})
            r.raise_for_status()
            raw = r.content
            if not raw or raw[:1] == b"{" or (len(raw) < 100 and b"<" not in raw):
                return None
            return raw
    except Exception:
        return None


def _text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def _parse_corpcode_xml(xml_bytes: bytes) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    root = ET.fromstring(xml_bytes)
    for list_el in root.findall(".//list"):
        corp_code = _text(list_el.find("corp_code"))
        corp_name = _text(list_el.find("corp_name"))
        stock_code = _text(list_el.find("stock_code"))[:6] if _text(list_el.find("stock_code")) else ""
        if corp_code and corp_name and stock_code:
            out.append({
                "corp_code": corp_code,
                "corp_name": corp_name,
                "stock_code": stock_code,
            })
    return out


def refresh_corp_code_cache(session: Session) -> tuple[bool, int]:
    """DART에서 고유번호 ZIP 다운로드 후 DB에 저장. 상장사만. (성공 여부, 저장 건수)."""
    raw = _fetch_zip()
    if not raw:
        return False, 0
    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as z:
            names = z.namelist()
            xml_name = next((n for n in names if n.lower().endswith(".xml")), names[0] if names else None)
            if not xml_name:
                return False, 0
            with z.open(xml_name) as f:
                xml_bytes = f.read()
    except Exception:
        return False, 0
    rows = _parse_corpcode_xml(xml_bytes)
    session.exec(delete(CorpCodeCache))
    for r in rows:
        session.add(CorpCodeCache(corp_code=r["corp_code"], corp_name=r["corp_name"], stock_code=r["stock_code"]))
    today = _today_kst()
    existing = session.exec(select(AppSetting).where(AppSetting.key == CACHE_DATE_KEY)).first()
    if existing:
        existing.value = today
        session.add(existing)
    else:
        session.add(AppSetting(key=CACHE_DATE_KEY, value=today))
    session.commit()
    return True, len(rows)


def is_cache_fresh(session: Session) -> bool:
    """오늘 이미 갱신했으면 True."""
    row = session.exec(select(AppSetting).where(AppSetting.key == CACHE_DATE_KEY)).first()
    if not row:
        return False
    return row.value == _today_kst()


def search_from_db(session: Session, query: str, limit: int = 30) -> list[dict[str, Any]]:
    """종목명으로 DB 검색. 캐시가 오늘 갱신되지 않았으면 먼저 갱신."""
    q = (query or "").strip()
    if not q:
        return []
    if not is_cache_fresh(session):
        refresh_corp_code_cache(session)
    like = f"%{q}%"
    stmt = (
        select(CorpCodeCache)
        .where(col(CorpCodeCache.corp_name).like(like))
        .order_by(CorpCodeCache.corp_name)
        .limit(limit)
    )
    rows = session.exec(stmt).all()
    return [
        {"corp_code": r.corp_code, "corp_name": r.corp_name, "stock_code": r.stock_code}
        for r in rows
    ]
