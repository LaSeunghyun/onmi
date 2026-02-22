from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from .models import (
    AdminAuditLog,
    AdminUser,
    AppSetting,
    MemberAccessLog,
    MemberActionLog,
    MemberProfile,
)
from .security import hash_password


def _now() -> datetime:
    return datetime.now().astimezone()


def ensure_default_admin(session: Session) -> AdminUser:
    row = session.exec(select(AdminUser).where(AdminUser.admin_id == "admin")).first()
    if row:
        return row

    now = _now()
    row = AdminUser(
        admin_id="admin",
        password_hash=hash_password("1234"),
        role="super_admin",
        must_change_password=True,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def ensure_member_profile(session: Session, user_id: UUID) -> MemberProfile:
    row = session.exec(select(MemberProfile).where(MemberProfile.user_id == user_id)).first()
    if row:
        return row

    row = MemberProfile(user_id=user_id, status="active", points=0, updated_at=_now())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def write_member_access_log(
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
        created_at=_now(),
    )
    session.add(row)
    session.commit()


def write_member_action_log(
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
        created_at=_now(),
    )
    session.add(row)
    session.commit()


def write_admin_audit_log(
    session: Session,
    *,
    admin_user_id: UUID,
    action_type: str,
    target_type: str,
    target_id: UUID | None = None,
    reason: str | None = None,
    before_obj: dict[str, Any] | None = None,
    after_obj: dict[str, Any] | None = None,
) -> None:
    row = AdminAuditLog(
        admin_user_id=admin_user_id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        before_json=json.dumps(before_obj, ensure_ascii=False) if before_obj else None,
        after_json=json.dumps(after_obj, ensure_ascii=False) if after_obj else None,
        created_at=_now(),
    )
    session.add(row)
    session.commit()


def get_setting(session: Session, key: str, default_value: str) -> str:
    row = session.exec(select(AppSetting).where(AppSetting.key == key)).first()
    if row:
        return row.value

    row = AppSetting(key=key, value=default_value, updated_at=_now())
    session.add(row)
    session.commit()
    return default_value


def set_setting(session: Session, key: str, value: str) -> None:
    row = session.exec(select(AppSetting).where(AppSetting.key == key)).first()
    now = _now()
    if not row:
        row = AppSetting(key=key, value=value, updated_at=now)
        session.add(row)
    else:
        row.value = value
        row.updated_at = now
        session.add(row)
    session.commit()
