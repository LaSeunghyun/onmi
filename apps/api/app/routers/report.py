from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, and_, select

from ..collect import kst_date_today
from ..db import get_session
from ..deps import get_current_user
from ..models import Article, ArticleKeyword, Keyword, ProcessingResult, User


router = APIRouter(prefix="/report", tags=["report"])


class KeywordCount(BaseModel):
    id: UUID
    text: str
    is_pinned: bool
    count: int


class ReportItem(BaseModel):
    article_id: UUID
    keyword_id: Optional[UUID]
    keyword_text: Optional[str]
    title: str
    source_name: Optional[str]
    published_at: Optional[str]
    sentiment: Optional[str]
    summary_ko: Optional[str]
    translation_status: Optional[str]
    original_url: str


class ReportResponse(BaseModel):
    date_kst: str
    keywords: list[KeywordCount]
    total_articles: int
    items: list[ReportItem]


def _parse_date(d: str | None) -> date:
    if not d:
        return kst_date_today()
    try:
        return date.fromisoformat(d)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid date (expected YYYY-MM-DD)")


@router.get("", response_model=ReportResponse)
def get_report(
    date_kst: str | None = Query(default=None),
    keyword_id: UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReportResponse:
    day = _parse_date(date_kst)
    day_str = day.isoformat()

    # keyword chip counts (for this date)
    kw_rows = session.exec(select(Keyword).where(Keyword.user_id == user.id)).all()
    counts: dict[UUID, int] = {k.id: 0 for k in kw_rows}

    ak = session.exec(
        select(ArticleKeyword, Article)
        .join(Article, ArticleKeyword.article_id == Article.id)
        .where(and_(Article.user_id == user.id, Article.date_kst == day_str))
    ).all()
    for link, _a in ak:
        if link.keyword_id in counts:
            counts[link.keyword_id] += 1

    kw_counts = [
        KeywordCount(id=k.id, text=k.text, is_pinned=k.is_pinned, count=counts.get(k.id, 0))
        for k in kw_rows
        if counts.get(k.id, 0) > 0
    ]
    kw_counts.sort(key=lambda x: (not x.is_pinned, -x.count, x.text.lower()))

    # articles list
    stmt = select(Article).where(and_(Article.user_id == user.id, Article.date_kst == day_str))
    if keyword_id:
        stmt = (
            select(Article)
            .join(ArticleKeyword, ArticleKeyword.article_id == Article.id)
            .where(and_(Article.user_id == user.id, Article.date_kst == day_str, ArticleKeyword.keyword_id == keyword_id))
        )
    articles = session.exec(stmt.order_by(Article.published_at.desc().nullslast(), Article.fetched_at.desc())).all()

    items: list[ReportItem] = []
    for a in articles:
        pr = session.exec(
            select(ProcessingResult).where(and_(ProcessingResult.user_id == user.id, ProcessingResult.article_id == a.id))
        ).first()

        # choose primary keyword for display
        if keyword_id:
            kw = session.exec(select(Keyword).where(and_(Keyword.user_id == user.id, Keyword.id == keyword_id))).first()
        else:
            links = session.exec(select(ArticleKeyword).where(ArticleKeyword.article_id == a.id)).all()
            kw_ids = [l.keyword_id for l in links]
            kws = (
                session.exec(select(Keyword).where(and_(Keyword.user_id == user.id, Keyword.id.in_(kw_ids))))
                .all()
                if kw_ids
                else []
            )
            kws.sort(key=lambda k: (not k.is_pinned, k.text.lower()))
            kw = kws[0] if kws else None

        items.append(
            ReportItem(
                article_id=a.id,
                keyword_id=kw.id if kw else None,
                keyword_text=kw.text if kw else None,
                title=a.title_original,
                source_name=a.source_name,
                published_at=a.published_at.isoformat() if a.published_at else None,
                sentiment=pr.sentiment if pr else None,
                summary_ko=pr.summary_ko if pr else None,
                translation_status=pr.translation_status if pr else None,
                original_url=a.original_url,
            )
        )

    return ReportResponse(
        date_kst=day_str,
        keywords=kw_counts,
        total_articles=len(items),
        items=items,
    )

