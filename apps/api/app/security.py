from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .settings import settings


# NOTE:
# Windows 환경에서 bcrypt/패스라이브 버전 조합 이슈가 빈번해,
# Step 8에서는 안정적인 PBKDF2를 기본 해시로 사용합니다.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(
    *,
    sub: str,
    expires_minutes: Optional[int] = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(minutes=expires_minutes or settings.access_token_expires_minutes)
    payload: dict[str, Any] = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise ValueError("invalid token") from e

