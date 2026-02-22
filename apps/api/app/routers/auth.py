from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from ..admin_ops import ensure_member_profile, write_member_access_log
from ..db import get_session, init_db
from ..models import User
from ..security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(body: SignupRequest, session: Session = Depends(get_session)) -> TokenResponse:
    init_db()
    existing = session.exec(select(User).where(User.email == str(body.email))).first()
    if existing:
        raise HTTPException(status_code=409, detail="email already exists")

    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="password too short")

    now = datetime.now().astimezone()
    user = User(
        email=str(body.email),
        password_hash=hash_password(body.password),
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    ensure_member_profile(session, user.id)

    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> TokenResponse:
    init_db()
    user = session.exec(select(User).where(User.email == str(body.email))).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    ensure_member_profile(session, user.id)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    write_member_access_log(
        session,
        user_id=user.id,
        event_type="login_success",
        ip=ip,
        user_agent=user_agent,
    )

    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token)

