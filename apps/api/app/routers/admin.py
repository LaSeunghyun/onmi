from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, col, select

from ..admin_ops import (
    ensure_member_profile,
    get_setting,
    set_setting,
    write_admin_audit_log,
)
from ..db import get_session, init_db
from ..deps_admin import get_current_admin
from ..models import (
    AdminAuditLog,
    AdminUser,
    Keyword,
    MemberAccessLog,
    MemberActionLog,
    MemberProfile,
    PointAdjustmentRequest,
    ServiceModule,
    User,
)
from ..security import hash_password


router = APIRouter(prefix="/admin", tags=["admin"])


class MemberStatusUpdateRequest(BaseModel):
    status: str  # active | suspended
    reason: str | None = None


class PointAdjustRequest(BaseModel):
    amount: int
    reason: str


class MemberCreateRequest(BaseModel):
    email: str
    password: str
    status: str = "active"
    initial_points: int = 0


class ModuleCreateRequest(BaseModel):
    module_key: str
    name: str
    route_path: str
    description: str | None = None
    is_active: bool = True


class ModuleUpdateRequest(BaseModel):
    name: str | None = None
    route_path: str | None = None
    description: str | None = None
    is_active: bool | None = None


class LogRetentionUpdateRequest(BaseModel):
    value: str  # permanent | days:<n>


def _parse_json(text: str | None) -> dict | None:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


@router.post("/members", response_model=dict, status_code=201)
def create_member(
    body: MemberCreateRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    email = body.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="invalid email")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="password too short")
    if body.status not in {"active", "suspended"}:
        raise HTTPException(status_code=400, detail="invalid status")
    if body.initial_points < 0:
        raise HTTPException(status_code=400, detail="initial_points must be >= 0")

    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="email already exists")

    now = datetime.now().astimezone()
    user = User(
        email=email,
        password_hash=hash_password(body.password),
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    profile = ensure_member_profile(session, user.id)
    profile.status = body.status
    profile.points = body.initial_points
    profile.updated_at = now
    session.add(profile)
    session.commit()
    session.refresh(profile)

    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="member_create",
        target_type="user",
        target_id=user.id,
        after_obj={
            "email": user.email,
            "status": profile.status,
            "points": profile.points,
        },
    )
    return {"id": str(user.id), "email": user.email}


@router.get("/members", response_model=list[dict])
def list_members(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    status_filter: str = Query(default="all"),
    limit: int = Query(default=50, ge=1, le=200),
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> list[dict]:
    init_db()
    _ = admin

    stmt = select(User).order_by(User.created_at.desc()).limit(limit)
    if q:
        stmt = stmt.where(col(User.email).like(f"%{q}%"))
    users = session.exec(stmt).all()

    rows: list[dict] = []
    for u in users:
        profile = ensure_member_profile(session, u.id)
        if status_filter != "all" and profile.status != status_filter:
            continue
        rows.append(
            {
                "id": str(u.id),
                "email": u.email,
                "created_at": u.created_at.isoformat(),
                "status": profile.status,
                "points": profile.points,
            }
        )
    return rows


@router.get("/members/{user_id}", response_model=dict)
def get_member_detail(
    user_id: UUID,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    _ = admin

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="member not found")

    profile = ensure_member_profile(session, user.id)
    keywords = session.exec(select(Keyword).where(Keyword.user_id == user.id)).all()
    access_logs = session.exec(
        select(MemberAccessLog).where(MemberAccessLog.user_id == user.id).order_by(MemberAccessLog.created_at.desc()).limit(100)
    ).all()
    action_logs = session.exec(
        select(MemberActionLog).where(MemberActionLog.user_id == user.id).order_by(MemberActionLog.created_at.desc()).limit(200)
    ).all()

    return {
        "member": {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "status": profile.status,
            "points": profile.points,
        },
        "keywords": [
            {
                "id": str(k.id),
                "text": k.text,
                "is_active": k.is_active,
                "is_pinned": k.is_pinned,
                "updated_at": k.updated_at.isoformat(),
            }
            for k in keywords
        ],
        "access_logs": [
            {
                "event_type": l.event_type,
                "ip": l.ip,
                "user_agent": l.user_agent,
                "created_at": l.created_at.isoformat(),
            }
            for l in access_logs
        ],
        "action_logs": [
            {
                "action_type": l.action_type,
                "entity_type": l.entity_type,
                "entity_id": str(l.entity_id) if l.entity_id else None,
                "details": _parse_json(l.details_json),
                "created_at": l.created_at.isoformat(),
            }
            for l in action_logs
        ],
    }


@router.patch("/members/{user_id}/status", response_model=dict)
def update_member_status(
    user_id: UUID,
    body: MemberStatusUpdateRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    if body.status not in {"active", "suspended"}:
        raise HTTPException(status_code=400, detail="invalid status")

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="member not found")
    profile = ensure_member_profile(session, user.id)
    before = {"status": profile.status}

    profile.status = body.status
    profile.updated_at = datetime.now().astimezone()
    session.add(profile)
    session.commit()
    session.refresh(profile)

    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="member_status_update",
        target_type="member_profile",
        target_id=profile.id,
        reason=body.reason,
        before_obj=before,
        after_obj={"status": profile.status},
    )
    return {"status": "ok", "member_status": profile.status}


@router.post("/members/{user_id}/points/adjust", response_model=dict)
def request_point_adjustment(
    user_id: UUID,
    body: PointAdjustRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    if not body.reason.strip():
        raise HTTPException(status_code=400, detail="reason is required")
    if abs(body.amount) > 100000:
        raise HTTPException(status_code=400, detail="single adjustment limit exceeded (100000)")

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="member not found")
    profile = ensure_member_profile(session, user.id)

    now = datetime.now().astimezone()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_reqs = session.exec(
        select(PointAdjustmentRequest)
        .where(PointAdjustmentRequest.requested_by_admin_id == admin.id)
        .where(PointAdjustmentRequest.created_at >= today_start)
    ).all()
    today_total = sum(abs(r.amount) for r in today_reqs if r.status in {"requested", "approved", "applied"})
    if today_total + abs(body.amount) > 500000:
        raise HTTPException(status_code=400, detail="daily adjustment limit exceeded (500000)")

    req = PointAdjustmentRequest(
        member_user_id=user.id,
        amount=body.amount,
        reason=body.reason.strip(),
        requested_by_admin_id=admin.id,
        status="requested",
        created_at=now,
        updated_at=now,
    )
    session.add(req)
    session.commit()
    session.refresh(req)

    if abs(body.amount) <= 10000:
        before = {"points": profile.points}
        profile.points += body.amount
        profile.updated_at = now
        req.status = "applied"
        req.approved_by_admin_id = admin.id
        req.updated_at = now
        session.add(profile)
        session.add(req)
        session.commit()
        session.refresh(profile)
        session.refresh(req)

        write_admin_audit_log(
            session,
            admin_user_id=admin.id,
            action_type="member_points_applied",
            target_type="member_profile",
            target_id=profile.id,
            reason=body.reason,
            before_obj=before,
            after_obj={"points": profile.points, "amount": body.amount},
        )
        return {"request_id": str(req.id), "status": "applied", "points": profile.points}

    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="member_points_requested",
        target_type="point_adjustment_request",
        target_id=req.id,
        reason=body.reason,
        after_obj={"amount": body.amount, "status": "requested"},
    )
    return {"request_id": str(req.id), "status": "requested"}


@router.post("/point-adjustments/{request_id}/approve", response_model=dict)
def approve_point_adjustment(
    request_id: UUID,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    req = session.exec(select(PointAdjustmentRequest).where(PointAdjustmentRequest.id == request_id)).first()
    if not req:
        raise HTTPException(status_code=404, detail="point request not found")
    if req.status != "requested":
        raise HTTPException(status_code=400, detail="point request already processed")
    if req.requested_by_admin_id == admin.id:
        raise HTTPException(status_code=400, detail="requester cannot self-approve")

    profile = ensure_member_profile(session, req.member_user_id)
    before = {"points": profile.points}
    now = datetime.now().astimezone()
    profile.points += req.amount
    profile.updated_at = now
    req.status = "applied"
    req.approved_by_admin_id = admin.id
    req.updated_at = now
    session.add(profile)
    session.add(req)
    session.commit()
    session.refresh(profile)

    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="member_points_approved_and_applied",
        target_type="point_adjustment_request",
        target_id=req.id,
        reason=req.reason,
        before_obj=before,
        after_obj={"points": profile.points, "amount": req.amount},
    )
    return {"status": "applied", "points": profile.points}


@router.get("/modules", response_model=list[dict])
def list_modules(
    include_inactive: bool = Query(default=True),
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> list[dict]:
    init_db()
    _ = admin
    stmt = select(ServiceModule).order_by(ServiceModule.updated_at.desc())
    if not include_inactive:
        stmt = stmt.where(ServiceModule.is_active == True)  # noqa: E712
    rows = session.exec(stmt).all()
    return [
        {
            "id": str(m.id),
            "module_key": m.module_key,
            "name": m.name,
            "route_path": m.route_path,
            "description": m.description,
            "is_active": m.is_active,
            "updated_at": m.updated_at.isoformat(),
        }
        for m in rows
    ]


@router.post("/modules", response_model=dict, status_code=201)
def create_module(
    body: ModuleCreateRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    exists = session.exec(select(ServiceModule).where(ServiceModule.module_key == body.module_key)).first()
    if exists:
        raise HTTPException(status_code=409, detail="module_key already exists")
    now = datetime.now().astimezone()
    row = ServiceModule(
        module_key=body.module_key.strip(),
        name=body.name.strip(),
        route_path=body.route_path.strip(),
        description=(body.description or "").strip() or None,
        is_active=body.is_active,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="module_create",
        target_type="service_module",
        target_id=row.id,
        after_obj={
            "module_key": row.module_key,
            "name": row.name,
            "route_path": row.route_path,
            "is_active": row.is_active,
        },
    )
    return {"id": str(row.id)}


@router.patch("/modules/{module_id}", response_model=dict)
def update_module(
    module_id: UUID,
    body: ModuleUpdateRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    row = session.exec(select(ServiceModule).where(ServiceModule.id == module_id)).first()
    if not row:
        raise HTTPException(status_code=404, detail="module not found")

    before = {
        "name": row.name,
        "route_path": row.route_path,
        "description": row.description,
        "is_active": row.is_active,
    }
    changed = False
    if body.name is not None and body.name.strip() != row.name:
        row.name = body.name.strip()
        changed = True
    if body.route_path is not None and body.route_path.strip() != row.route_path:
        row.route_path = body.route_path.strip()
        changed = True
    if body.description is not None:
        next_desc = body.description.strip() or None
        if next_desc != row.description:
            row.description = next_desc
            changed = True
    if body.is_active is not None and body.is_active != row.is_active:
        row.is_active = body.is_active
        changed = True
    if not changed:
        return {"status": "noop"}

    row.updated_at = datetime.now().astimezone()
    session.add(row)
    session.commit()
    session.refresh(row)

    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="module_update",
        target_type="service_module",
        target_id=row.id,
        before_obj=before,
        after_obj={
            "name": row.name,
            "route_path": row.route_path,
            "description": row.description,
            "is_active": row.is_active,
        },
    )
    return {"status": "ok"}


@router.delete("/modules/{module_id}", status_code=204)
def delete_module(
    module_id: UUID,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> None:
    init_db()
    row = session.exec(select(ServiceModule).where(ServiceModule.id == module_id)).first()
    if not row:
        raise HTTPException(status_code=404, detail="module not found")
    before = {
        "module_key": row.module_key,
        "name": row.name,
        "route_path": row.route_path,
        "is_active": row.is_active,
    }
    session.delete(row)
    session.commit()
    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="module_delete",
        target_type="service_module",
        target_id=module_id,
        before_obj=before,
    )
    return None


@router.get("/audit-logs", response_model=list[dict])
def list_audit_logs(
    limit: int = Query(default=200, ge=1, le=500),
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> list[dict]:
    init_db()
    _ = admin
    rows = session.exec(select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit)).all()
    return [
        {
            "id": str(r.id),
            "admin_user_id": str(r.admin_user_id),
            "action_type": r.action_type,
            "target_type": r.target_type,
            "target_id": str(r.target_id) if r.target_id else None,
            "reason": r.reason,
            "before": _parse_json(r.before_json),
            "after": _parse_json(r.after_json),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/settings/log-retention", response_model=dict)
def get_log_retention_setting(
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    _ = admin
    value = get_setting(session, "log_retention", "permanent")
    return {"key": "log_retention", "value": value}


@router.put("/settings/log-retention", response_model=dict)
def update_log_retention_setting(
    body: LogRetentionUpdateRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    init_db()
    value = body.value.strip().lower()
    if value != "permanent":
        if not value.startswith("days:"):
            raise HTTPException(status_code=400, detail="value must be permanent or days:<n>")
        try:
            days = int(value.split(":", 1)[1])
        except Exception:
            raise HTTPException(status_code=400, detail="invalid days value")
        if days < 1:
            raise HTTPException(status_code=400, detail="days must be >= 1")

    before = get_setting(session, "log_retention", "permanent")
    set_setting(session, "log_retention", value)
    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="log_retention_update",
        target_type="app_setting",
        reason="admin setting change",
        before_obj={"value": before},
        after_obj={"value": value},
    )
    return {"key": "log_retention", "value": value}
