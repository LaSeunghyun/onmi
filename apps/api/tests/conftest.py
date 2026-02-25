"""공용 pytest 픽스처.

각 테스트는 독립된 인메모리 SQLite DB를 사용하므로
테스트 간 데이터 오염이 없습니다.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app

# ---------------------------------------------------------------------------
# 공용 상수
# ---------------------------------------------------------------------------
SIGNUP_EMAIL = "user@test.com"
SIGNUP_PASSWORD = "testpass123"

ADMIN_ID = "admin"
ADMIN_PASSWORD = "1234"


# ---------------------------------------------------------------------------
# 기본 픽스처
# ---------------------------------------------------------------------------


@pytest.fixture(name="client")
def client_fixture():
    """테스트마다 새 인메모리 DB + TestClient 를 생성합니다."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app, raise_server_exceptions=True)
    yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 인증 헬퍼 픽스처
# ---------------------------------------------------------------------------


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient) -> dict[str, str]:
    """일반 사용자 회원가입 후 Authorization 헤더를 반환합니다."""
    resp = client.post(
        "/auth/signup",
        json={"email": SIGNUP_EMAIL, "password": SIGNUP_PASSWORD},
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(client: TestClient) -> dict[str, str]:
    """기본 관리자(admin/1234) 로그인 후 Authorization 헤더를 반환합니다."""
    resp = client.post(
        "/admin/auth/login",
        json={"admin_id": ADMIN_ID, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
