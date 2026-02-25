"""사용자 인증·멤버 관리 Application Service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ...security import create_access_token, hash_password, verify_password
from .models import MemberAccessLog, MemberActionLog, MemberProfile, User


class UserService:
    @staticmethod
    def signup(session: Session, email: str, password: str) -> tuple[User, str]:
        """회원가입. (user, access_token) 반환."""
        email = email.strip().lower()
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise HTTPException(status_code=409, detail="email already exists")
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="password too short")

        now = datetime.now().astimezone()
        user = User(
            email=email,
            password_hash=hash_password(password),
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        MemberService.ensure_profile(session, user.id)
        token = create_access_token(sub=str(user.id))
        return user, token

    @staticmethod
    def authenticate(session: Session, email: str, password: str) -> tuple[User, str]:
        """로그인. (user, access_token) 반환."""
        email = email.strip().lower()
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid credentials",
            )
        MemberService.ensure_profile(session, user.id)
        token = create_access_token(sub=str(user.id))
        return user, token

    @staticmethod
    def get_by_id(session: Session, user_id: UUID) -> User | None:
        return session.exec(select(User).where(User.id == user_id)).first()


class MemberService:
    @staticmethod
    def ensure_profile(session: Session, user_id: UUID) -> MemberProfile:
        row = session.exec(select(MemberProfile).where(MemberProfile.user_id == user_id)).first()
        if row:
            return row
        row = MemberProfile(user_id=user_id, status="active", points=0, updated_at=datetime.now().astimezone())
        session.add(row)
        session.commit()
        session.refresh(row)
        return row

    @staticmethod
    def write_access_log(
        session: Session,
        *,
        user_id: UUID,
        event_type: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        row = MemberAccessLog(
            user_id=user_id,
            event_type=event_type,
            ip=ip,
            user_agent=user_agent,
            created_at=datetime.now().astimezone(),
        )
        session.add(row)
        session.commit()

    @staticmethod
    def write_action_log(
        session: Session,
        *,
        user_id: UUID,
        action_type: str,
        entity_type: str,
        entity_id: UUID | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        row = MemberActionLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details_json=json.dumps(details, ensure_ascii=False) if details else None,
            created_at=datetime.now().astimezone(),
        )
        session.add(row)
        session.commit()
