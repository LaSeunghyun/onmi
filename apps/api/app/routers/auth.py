from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from ..db import get_session
from ..domains.identity.schemas import LoginRequest, SignupRequest, TokenResponse
from ..domains.identity.service import MemberService, UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(body: SignupRequest, session: Session = Depends(get_session)) -> TokenResponse:
    _user, token = UserService.signup(session, str(body.email), body.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> TokenResponse:
    user, token = UserService.authenticate(session, str(body.email), body.password)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    MemberService.write_access_log(
        session,
        user_id=user.id,
        event_type="login_success",
        ip=ip,
        user_agent=user_agent,
    )
    return TokenResponse(access_token=token)
