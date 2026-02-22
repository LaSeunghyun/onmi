from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, and_, select

from ..collect import kst_date_today, rss_google_news, search_gdelt
from ..db import get_session, init_db
from ..deps import get_current_user
from ..models import Article, ArticleKeyword, Keyword, User


router = APIRouter(prefix="/collect", tags=["collect"])


class CollectResponse(BaseModel):
    date_kst: str
    keywords_processed: int
    search_items: int
    rss_items: int
    inserted_articles: int
    linked_existing_articles: int


def _parse_date(d: Optional[str]) -> date:
    if not d:
        return kst_date_today()
    try:
        return date.fromisoformat(d)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid date (expected YYYY-MM-DD)")


@router.post("", response_model=CollectResponse)
async def collect_today(
    date_kst: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> CollectResponse:
    init_db()
    day = _parse_date(date_kst)
    day_str = day.isoformat()

    keywords = session.exec(
        select(Keyword).where(and_(Keyword.user_id == user.id, Keyword.is_active == True))  # noqa: E712
    ).all()

    inserted = 0
    linked = 0
    search_count = 0
    rss_count = 0

    for kw in keywords:
        used_rss = False
        items = []
        try:
            items = await search_gdelt(keyword=kw.text, day=day)
            search_count += len(items)
        except Exception:
            items = []

        if not items:
            used_rss = True
            try:
                rss_items = await rss_google_news(keyword=kw.text, day=day)
                rss_count += len(rss_items)
                items = rss_items
            except Exception:
                items = []

        for it in items:
            existing = session.exec(
                select(Article).where(and_(Article.user_id == user.id, Article.canonical_url == it.canonical_url))
            ).first()
            if existing:
                article = existing
                linked += 1
            else:
                article = Article(
                    user_id=user.id,
                    date_kst=day_str,
                    canonical_url=it.canonical_url,
                    original_url=it.url,
                    source_type=it.source_type,
                    source_name=it.source_name,
                    published_at=it.published_at,
                    fetched_at=datetime.now().astimezone(),
                    title_original=it.title,
                    snippet_original=it.snippet,
                    language_original=it.language,
                )
                session.add(article)
                session.commit()
                session.refresh(article)
                inserted += 1

            # Link article ↔ keyword (deduped by unique constraint)
            try:
                link_row = ArticleKeyword(article_id=article.id, keyword_id=kw.id)
                session.add(link_row)
                session.commit()
            except Exception:
                session.rollback()

    return CollectResponse(
        date_kst=day_str,
        keywords_processed=len(keywords),
        search_items=search_count,
        rss_items=rss_count,
        inserted_articles=inserted,
        linked_existing_articles=linked,
    )

