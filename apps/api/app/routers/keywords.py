from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, and_, col, select

from ..admin_ops import write_member_action_log
from ..db import get_session, init_db
from ..deps import get_current_user
from ..models import Keyword, KeywordPublic, User


router = APIRouter(prefix="/keywords", tags=["keywords"])


def _normalize_keyword(text: str) -> str:
    t = " ".join(text.strip().split())
    return t


class KeywordCreate(BaseModel):
    text: str
    is_active: bool = True


class KeywordUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_pinned: Optional[bool] = None


@router.get("", response_model=list[KeywordPublic])
def list_keywords(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    status_filter: Literal["all", "active", "inactive"] = "all",
    sort: Literal["pinned_recent", "recent", "alpha"] = "pinned_recent",
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[KeywordPublic]:
    init_db()
    stmt = select(Keyword).where(Keyword.user_id == user.id)
    if status_filter == "active":
        stmt = stmt.where(Keyword.is_active == True)  # noqa: E712
    elif status_filter == "inactive":
        stmt = stmt.where(Keyword.is_active == False)  # noqa: E712

    if q:
        like = f"%{q}%"
        stmt = stmt.where(col(Keyword.text).like(like))

    if sort == "alpha":
        stmt = stmt.order_by(Keyword.text.asc())
    elif sort == "recent":
        stmt = stmt.order_by(Keyword.updated_at.desc())
    else:
        stmt = stmt.order_by(Keyword.is_pinned.desc(), Keyword.updated_at.desc())

    rows = session.exec(stmt).all()
    return [KeywordPublic.model_validate(r) for r in rows]


@router.post("", response_model=KeywordPublic, status_code=201)
def create_keyword(
    body: KeywordCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> KeywordPublic:
    init_db()
    text = _normalize_keyword(body.text)
    if len(text) < 1:
        raise HTTPException(status_code=400, detail="keyword is empty")

    existing = session.exec(
        select(Keyword).where(and_(Keyword.user_id == user.id, Keyword.text == text))
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="keyword already exists")

    now = datetime.now().astimezone()
    kw = Keyword(
        user_id=user.id,
        text=text,
        is_active=body.is_active,
        created_at=now,
        updated_at=now,
    )
    session.add(kw)
    session.commit()
    session.refresh(kw)
    write_member_action_log(
        session,
        user_id=user.id,
        action_type="keyword_create",
        entity_type="keyword",
        entity_id=kw.id,
        details={"text": kw.text, "is_active": kw.is_active},
    )
    return KeywordPublic.model_validate(kw)


@router.patch("/{keyword_id}", response_model=KeywordPublic)
def update_keyword(
    keyword_id: UUID,
    body: KeywordUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> KeywordPublic:
    init_db()
    kw = session.exec(select(Keyword).where(and_(Keyword.id == keyword_id, Keyword.user_id == user.id))).first()
    if not kw:
        raise HTTPException(status_code=404, detail="keyword not found")

    changed = False
    before_snapshot = {"is_active": kw.is_active, "is_pinned": kw.is_pinned}
    now = datetime.now().astimezone()
    if body.is_active is not None and body.is_active != kw.is_active:
        kw.is_active = body.is_active
        changed = True
    if body.is_pinned is not None and body.is_pinned != kw.is_pinned:
        kw.is_pinned = body.is_pinned
        changed = True

    if changed:
        kw.updated_at = now
        session.add(kw)
        session.commit()
        session.refresh(kw)
        write_member_action_log(
            session,
            user_id=user.id,
            action_type="keyword_update",
            entity_type="keyword",
            entity_id=kw.id,
            details={
                "before": before_snapshot,
                "after": {"is_active": kw.is_active, "is_pinned": kw.is_pinned},
            },
        )

    return KeywordPublic.model_validate(kw)


@router.delete("/{keyword_id}", status_code=204)
def delete_keyword(
    keyword_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    init_db()
    kw = session.exec(select(Keyword).where(and_(Keyword.id == keyword_id, Keyword.user_id == user.id))).first()
    if not kw:
        raise HTTPException(status_code=404, detail="keyword not found")
    deleted_id = kw.id
    deleted_text = kw.text
    session.delete(kw)
    session.commit()
    write_member_action_log(
        session,
        user_id=user.id,
        action_type="keyword_delete",
        entity_type="keyword",
        entity_id=deleted_id,
        details={"text": deleted_text},
    )
    return None

