"""뉴스 키워드 Application Service."""
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, and_, col, select

from .models import Keyword
from .schemas import KeywordPublic


def _normalize(text: str) -> str:
    return " ".join(text.strip().split())


class KeywordService:
    @staticmethod
    def list_keywords(
        session: Session,
        user_id: UUID,
        q: str | None = None,
        status_filter: Literal["all", "active", "inactive"] = "all",
        sort: Literal["pinned_recent", "recent", "alpha"] = "pinned_recent",
    ) -> list[KeywordPublic]:
        stmt = select(Keyword).where(Keyword.user_id == user_id)
        if status_filter == "active":
            stmt = stmt.where(Keyword.is_active == True)  # noqa: E712
        elif status_filter == "inactive":
            stmt = stmt.where(Keyword.is_active == False)  # noqa: E712
        if q:
            stmt = stmt.where(col(Keyword.text).like(f"%{q}%"))
        if sort == "alpha":
            stmt = stmt.order_by(Keyword.text.asc())
        elif sort == "recent":
            stmt = stmt.order_by(Keyword.updated_at.desc())
        else:
            stmt = stmt.order_by(Keyword.is_pinned.desc(), Keyword.updated_at.desc())
        rows = session.exec(stmt).all()
        return [KeywordPublic.model_validate(r) for r in rows]

    @staticmethod
    def create(session: Session, user_id: UUID, text: str, is_active: bool) -> KeywordPublic:
        text = _normalize(text)
        if len(text) < 1:
            raise HTTPException(status_code=400, detail="keyword is empty")
        existing = session.exec(
            select(Keyword).where(and_(Keyword.user_id == user_id, Keyword.text == text))
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="keyword already exists")
        now = datetime.now().astimezone()
        kw = Keyword(user_id=user_id, text=text, is_active=is_active, created_at=now, updated_at=now)
        session.add(kw)
        session.commit()
        session.refresh(kw)
        return KeywordPublic.model_validate(kw)

    @staticmethod
    def update(
        session: Session,
        user_id: UUID,
        keyword_id: UUID,
        is_active: bool | None,
        is_pinned: bool | None,
    ) -> tuple[KeywordPublic, bool, dict]:
        """(updated_public, changed, before_snapshot) 반환."""
        kw = session.exec(select(Keyword).where(and_(Keyword.id == keyword_id, Keyword.user_id == user_id))).first()
        if not kw:
            raise HTTPException(status_code=404, detail="keyword not found")
        changed = False
        before_snapshot = {"is_active": kw.is_active, "is_pinned": kw.is_pinned}
        now = datetime.now().astimezone()
        if is_active is not None and is_active != kw.is_active:
            kw.is_active = is_active
            changed = True
        if is_pinned is not None and is_pinned != kw.is_pinned:
            kw.is_pinned = is_pinned
            changed = True
        if changed:
            kw.updated_at = now
            session.add(kw)
            session.commit()
            session.refresh(kw)
        return KeywordPublic.model_validate(kw), changed, before_snapshot

    @staticmethod
    def delete(session: Session, user_id: UUID, keyword_id: UUID) -> tuple[UUID, str]:
        """삭제 후 (deleted_id, deleted_text) 반환."""
        kw = session.exec(select(Keyword).where(and_(Keyword.id == keyword_id, Keyword.user_id == user_id))).first()
        if not kw:
            raise HTTPException(status_code=404, detail="keyword not found")
        deleted_id = kw.id
        deleted_text = kw.text
        session.delete(kw)
        session.commit()
        return deleted_id, deleted_text
