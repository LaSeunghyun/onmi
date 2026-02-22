from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, and_, select

from ..collect import kst_date_today
from ..db import get_session, init_db
from ..deps import get_current_user
from ..models import Article, ProcessingResult, User
from ..process import process_article


router = APIRouter(prefix="/process", tags=["process"])


class ProcessResponse(BaseModel):
    date_kst: str
    articles_total: int
    processed_new: int
    skipped_existing: int


def _parse_date(d: str | None) -> date:
    if not d:
        return kst_date_today()
    try:
        return date.fromisoformat(d)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid date (expected YYYY-MM-DD)")


@router.post("", response_model=ProcessResponse)
def process_day(
    date_kst: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProcessResponse:
    init_db()
    day = _parse_date(date_kst)
    day_str = day.isoformat()

    articles = session.exec(
        select(Article).where(and_(Article.user_id == user.id, Article.date_kst == day_str))
    ).all()

    processed_new = 0
    skipped = 0
    for a in articles:
        existing = session.exec(
            select(ProcessingResult).where(and_(ProcessingResult.user_id == user.id, ProcessingResult.article_id == a.id))
        ).first()
        if existing:
            skipped += 1
            continue

        p = process_article(a)
        row = ProcessingResult(
            user_id=user.id,
            article_id=a.id,
            sentiment=p.sentiment,
            sentiment_confidence=p.sentiment_confidence,
            summary_original=p.summary_original,
            summary_ko=p.summary_ko,
            translated_from=p.translated_from,
            translation_status=p.translation_status,
        )
        session.add(row)
        session.commit()
        processed_new += 1

    return ProcessResponse(
        date_kst=day_str,
        articles_total=len(articles),
        processed_new=processed_new,
        skipped_existing=skipped,
    )

