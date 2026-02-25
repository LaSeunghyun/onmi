from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..db import get_session
from ..deps import get_current_user
from ..domains.content.schemas import KeywordCreate, KeywordPublic, KeywordUpdate
from ..domains.content.service import KeywordService
from ..domains.identity.models import User
from ..domains.identity.service import MemberService

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("", response_model=list[KeywordPublic])
def list_keywords(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    status_filter: Literal["all", "active", "inactive"] = "all",
    sort: Literal["pinned_recent", "recent", "alpha"] = "pinned_recent",
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[KeywordPublic]:
    return KeywordService.list_keywords(session, user.id, q=q, status_filter=status_filter, sort=sort)


@router.post("", response_model=KeywordPublic, status_code=201)
def create_keyword(
    body: KeywordCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> KeywordPublic:
    kw = KeywordService.create(session, user.id, body.text, body.is_active)
    MemberService.write_action_log(
        session,
        user_id=user.id,
        action_type="keyword_create",
        entity_type="keyword",
        entity_id=kw.id,
        details={"text": kw.text, "is_active": kw.is_active},
    )
    return kw


@router.patch("/{keyword_id}", response_model=KeywordPublic)
def update_keyword(
    keyword_id: UUID,
    body: KeywordUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> KeywordPublic:
    kw, changed, before_snapshot = KeywordService.update(
        session, user.id, keyword_id, body.is_active, body.is_pinned
    )
    if changed:
        MemberService.write_action_log(
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
    return kw


@router.delete("/{keyword_id}", status_code=204)
def delete_keyword(
    keyword_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    deleted_id, deleted_text = KeywordService.delete(session, user.id, keyword_id)
    MemberService.write_action_log(
        session,
        user_id=user.id,
        action_type="keyword_delete",
        entity_type="keyword",
        entity_id=deleted_id,
        details={"text": deleted_text},
    )
    return None
