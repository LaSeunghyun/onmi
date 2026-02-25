from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from ..admin_ops import ensure_default_admin, write_admin_audit_log
from ..db import get_session
from ..deps_admin import get_current_admin
from ..models import AdminUser
from ..security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


class AdminLoginRequest(BaseModel):
    admin_id: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool
    role: str


class AdminChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=AdminTokenResponse)
def admin_login(body: AdminLoginRequest, session: Session = Depends(get_session)) -> AdminTokenResponse:
    ensure_default_admin(session)

    admin = session.exec(select(AdminUser).where(AdminUser.admin_id == body.admin_id)).first()
    if not admin or not admin.is_active or not verify_password(body.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid admin credentials")

    token = create_access_token(sub=str(admin.id), extra_claims={"typ": "admin", "role": admin.role})
    return AdminTokenResponse(
        access_token=token,
        must_change_password=admin.must_change_password,
        role=admin.role,
    )


@router.post("/change-password", response_model=dict)
def change_admin_password(
    body: AdminChangePasswordRequest,
    admin: AdminUser = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict:
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="password too short")
    if not verify_password(body.current_password, admin.password_hash):
        raise HTTPException(status_code=400, detail="current password mismatch")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="new password must be different")

    now = datetime.now().astimezone()
    before = {"must_change_password": admin.must_change_password}
    admin.password_hash = hash_password(body.new_password)
    admin.must_change_password = False
    admin.updated_at = now
    session.add(admin)
    session.commit()

    write_admin_audit_log(
        session,
        admin_user_id=admin.id,
        action_type="admin_password_changed",
        target_type="admin_user",
        target_id=admin.id,
        before_obj=before,
        after_obj={"must_change_password": False},
    )
    return {"status": "ok"}


@router.get("/me", response_model=dict)
def get_admin_me(admin: AdminUser = Depends(get_current_admin)) -> dict:
    return {
        "id": str(admin.id),
        "admin_id": admin.admin_id,
        "role": admin.role,
        "must_change_password": admin.must_change_password,
        "is_active": admin.is_active,
    }
