"""인증(Auth) 엔드포인트 E2E 테스트.

커버리지:
  POST /auth/signup
  POST /auth/login
  GET  /me
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 회원가입
# ---------------------------------------------------------------------------


def test_signup_success(client: TestClient):
    """정상 회원가입 → 201 + access_token 반환."""
    resp = client.post(
        "/auth/signup",
        json={"email": "new@example.com", "password": "securepass"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10


def test_signup_duplicate_email(client: TestClient):
    """동일 이메일 재가입 → 409."""
    payload = {"email": "dup@example.com", "password": "securepass"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_signup_short_password(client: TestClient):
    """8자 미만 비밀번호 → 400."""
    resp = client.post(
        "/auth/signup",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert resp.status_code == 400
    assert "short" in resp.json()["detail"]


def test_signup_invalid_email(client: TestClient):
    """유효하지 않은 이메일 형식 → 422."""
    resp = client.post(
        "/auth/signup",
        json={"email": "not-an-email", "password": "securepass"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 로그인
# ---------------------------------------------------------------------------


def test_login_success(client: TestClient):
    """회원가입 후 로그인 → 200 + access_token."""
    email, password = "login@example.com", "mypassword"
    client.post("/auth/signup", json={"email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    """잘못된 비밀번호 → 401."""
    client.post("/auth/signup", json={"email": "wp@example.com", "password": "correct123"})
    resp = client.post("/auth/login", json={"email": "wp@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email(client: TestClient):
    """미등록 이메일 → 401."""
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------


def test_get_me(client: TestClient, auth_headers: dict):
    """인증된 사용자 GET /me → 200 + 사용자 정보."""
    resp = client.get("/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert "email" in body
    assert body["email"] == "user@test.com"
    assert body["auth_provider"] == "email"


def test_get_me_no_token(client: TestClient):
    """토큰 없이 GET /me → 401."""
    resp = client.get("/me")
    assert resp.status_code == 401


def test_get_me_invalid_token(client: TestClient):
    """잘못된 토큰 GET /me → 401."""
    resp = client.get("/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
