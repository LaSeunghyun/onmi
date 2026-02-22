from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from zoneinfo import ZoneInfo

import feedparser
import httpx
from dateutil import parser as dtparser

from .settings import settings

try:
    KST = ZoneInfo("Asia/Seoul")
except Exception:
    # Windows에서 시스템 tzdata가 없을 수 있어, 고정 오프셋으로 폴백
    KST = timezone(timedelta(hours=9))


def kst_date_today() -> date:
    return datetime.now(tz=KST).date()


def kst_day_bounds_utc(d: date) -> tuple[datetime, datetime]:
    start_kst = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=KST)
    end_kst = start_kst + timedelta(days=1)
    return start_kst.astimezone(timezone.utc), end_kst.astimezone(timezone.utc)


def canonicalize_url(url: str) -> str:
    try:
        u = urlparse(url)
        q = [(k, v) for (k, v) in parse_qsl(u.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
        new_q = urlencode(q, doseq=True)
        return urlunparse((u.scheme, u.netloc, u.path, u.params, new_q, u.fragment))
    except Exception:
        return url


@dataclass(frozen=True)
class CollectedItem:
    url: str
    canonical_url: str
    title: str
    snippet: Optional[str]
    source_name: Optional[str]
    source_type: str  # search_api | rss
    language: Optional[str]
    published_at: Optional[datetime]


async def search_gdelt(*, keyword: str, day: date, max_records: int = 25) -> list[CollectedItem]:
    if settings.collector_mode.lower() == "mock":
        if "force_rss" in keyword.lower():
            return []
        now = datetime.now().astimezone()
        return [
            CollectedItem(
                url="https://example.com/mock/search/1",
                canonical_url="https://example.com/mock/search/1",
                title=f"[MOCK] {keyword} 검색 결과 1",
                snippet="Mock snippet",
                source_name="MockSearch",
                source_type="search_api",
                language="en",
                published_at=now,
            )
        ]
    start_utc, end_utc = kst_day_bounds_utc(day)
    # GDELT expects YYYYMMDDHHMMSS in UTC
    start = start_utc.strftime("%Y%m%d%H%M%S")
    end = (end_utc - timedelta(seconds=1)).strftime("%Y%m%d%H%M%S")

    params = {
        "query": keyword,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": str(max_records),
        "startdatetime": start,
        "enddatetime": end,
        "sort": "HybridRel",
    }
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    timeout = httpx.Timeout(30.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "touch/0.1"}) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    items: list[CollectedItem] = []
    for a in (data.get("articles") or []):
        link = a.get("url") or a.get("sourceUrl") or a.get("link")
        title = a.get("title") or ""
        if not link or not title:
            continue
        lang = a.get("language")
        source = a.get("sourceCountry") or a.get("source") or a.get("sourceCollection")
        snippet = a.get("seendate")  # fallback; many results don't include snippet
        published_at = None
        dt = a.get("seendate") or a.get("datetime") or a.get("date")
        if dt:
            try:
                published_at = dtparser.parse(str(dt))
            except Exception:
                published_at = None

        items.append(
            CollectedItem(
                url=link,
                canonical_url=canonicalize_url(link),
                title=title,
                snippet=None if snippet == title else None,
                source_name=str(source) if source else None,
                source_type="search_api",
                language=str(lang) if lang else None,
                published_at=published_at,
            )
        )
    return items


def _google_news_rss_urls(keyword: str) -> list[str]:
    q = httpx.QueryParams({"q": keyword, "hl": "ko", "gl": "KR", "ceid": "KR:ko"}).encode()
    q2 = httpx.QueryParams({"q": keyword, "hl": "en", "gl": "US", "ceid": "US:en"}).encode()
    return [
        f"https://news.google.com/rss/search?{q}",
        f"https://news.google.com/rss/search?{q2}",
    ]


async def rss_google_news(*, keyword: str, day: date, max_records: int = 25) -> list[CollectedItem]:
    if settings.collector_mode.lower() == "mock":
        now = datetime.now().astimezone()
        return [
            CollectedItem(
                url="https://example.com/mock/rss/1",
                canonical_url="https://example.com/mock/rss/1",
                title=f"[MOCK] {keyword} RSS 결과 1",
                snippet="Mock RSS summary",
                source_name="MockRSS",
                source_type="rss",
                language="ko",
                published_at=now,
            )
        ]
    start_utc, end_utc = kst_day_bounds_utc(day)

    urls = _google_news_rss_urls(keyword)
    out: list[CollectedItem] = []
    timeout = httpx.Timeout(30.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "touch/0.1"}) as client:
        for u in urls:
            try:
                r = await client.get(u)
                r.raise_for_status()
            except Exception:
                continue

            feed = feedparser.parse(r.text)
            for e in feed.entries[: max_records * 2]:
                link = getattr(e, "link", None)
                title = getattr(e, "title", None)
                if not link or not title:
                    continue

                published_at = None
                if getattr(e, "published", None):
                    try:
                        published_at = dtparser.parse(e.published)
                    except Exception:
                        published_at = None
                if published_at:
                    pub_utc = published_at.astimezone(timezone.utc) if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc)
                    if not (start_utc <= pub_utc < end_utc):
                        continue

                out.append(
                    CollectedItem(
                        url=link,
                        canonical_url=canonicalize_url(link),
                        title=title,
                        snippet=getattr(e, "summary", None),
                        source_name="GoogleNewsRSS",
                        source_type="rss",
                        language=None,
                        published_at=published_at,
                    )
                )
    # Dedup by canonical_url while preserving order
    seen: set[str] = set()
    deduped: list[CollectedItem] = []
    for it in out:
        if it.canonical_url in seen:
            continue
        seen.add(it.canonical_url)
        deduped.append(it)
    return deduped[:max_records]

