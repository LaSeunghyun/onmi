from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from .db import get_session, init_db
from .models import AdminUser
from .security import decode_token


admin_auth_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    creds: HTTPAuthorizationCredentials | None = Depends(admin_auth_scheme),
    session: Session = Depends(get_session),
) -> AdminUser:
    init_db()
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing admin token")
    try:
        payload = decode_token(creds.credentials)
        if payload.get("typ") != "admin":
            raise ValueError("not admin token")
        admin_id = UUID(str(payload.get("sub")))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid admin token")

    admin = session.exec(select(AdminUser).where(AdminUser.id == admin_id)).first()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid admin token")
    return admin
