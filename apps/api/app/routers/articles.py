from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, and_, select

from ..db import get_session
from ..deps import get_current_user
from ..models import Article, ArticleKeyword, Keyword, ProcessingResult, User


router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleDetail(BaseModel):
    id: UUID
    title: str
    source_name: Optional[str]
    published_at: Optional[str]
    original_url: str
    keyword_texts: list[str]
    sentiment: Optional[str]
    summary_ko: Optional[str]
    translation_status: Optional[str]


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(
    article_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ArticleDetail:
    a = session.exec(select(Article).where(and_(Article.user_id == user.id, Article.id == article_id))).first()
    if not a:
        raise HTTPException(status_code=404, detail="article not found")

    pr = session.exec(
        select(ProcessingResult).where(and_(ProcessingResult.user_id == user.id, ProcessingResult.article_id == a.id))
    ).first()
    links = session.exec(select(ArticleKeyword).where(ArticleKeyword.article_id == a.id)).all()
    kw_ids = [l.keyword_id for l in links]
    kws = (
        session.exec(select(Keyword).where(and_(Keyword.user_id == user.id, Keyword.id.in_(kw_ids)))).all()
        if kw_ids
        else []
    )
    kw_texts = sorted([k.text for k in kws])

    return ArticleDetail(
        id=a.id,
        title=a.title_original,
        source_name=a.source_name,
        published_at=a.published_at.isoformat() if a.published_at else None,
        original_url=a.original_url,
        keyword_texts=kw_texts,
        sentiment=pr.sentiment if pr else None,
        summary_ko=pr.summary_ko if pr else None,
        translation_status=pr.translation_status if pr else None,
    )

