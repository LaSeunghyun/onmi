"""하위 호환 re-export. 새 코드는 domains/admin/service.py 와 domains/identity/service.py 를 직접 사용하세요."""
from __future__ import annotations

from .domains.admin.service import AdminService
from .domains.identity.service import MemberService


def ensure_default_admin(session):
    return AdminService.ensure_default_admin(session)


def ensure_member_profile(session, user_id):
    return MemberService.ensure_profile(session, user_id)


def write_member_access_log(session, *, user_id, event_type, ip=None, user_agent=None):
    return MemberService.write_access_log(
        session, user_id=user_id, event_type=event_type, ip=ip, user_agent=user_agent
    )


def write_member_action_log(session, *, user_id, action_type, entity_type, entity_id=None, details=None):
    return MemberService.write_action_log(
        session,
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )


def write_admin_audit_log(session, *, admin_user_id, action_type, target_type, target_id=None, reason=None, before_obj=None, after_obj=None):
    return AdminService.write_audit_log(
        session,
        admin_user_id=admin_user_id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        before_obj=before_obj,
        after_obj=after_obj,
    )


def get_setting(session, key, default_value):
    return AdminService.get_setting(session, key, default_value)


def set_setting(session, key, value):
    return AdminService.set_setting(session, key, value)
