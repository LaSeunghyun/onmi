"""관리자 도메인 Application Service (구 admin_ops.py)."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from ...security import hash_password
from .models import AdminAuditLog, AdminUser, AppSetting


def _now() -> datetime:
    return datetime.now().astimezone()


class AdminService:
    @staticmethod
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

    @staticmethod
    def write_audit_log(
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

    @staticmethod
    def get_setting(session: Session, key: str, default_value: str) -> str:
        row = session.exec(select(AppSetting).where(AppSetting.key == key)).first()
        if row:
            return row.value
        row = AppSetting(key=key, value=default_value, updated_at=_now())
        session.add(row)
        session.commit()
        return default_value

    @staticmethod
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
