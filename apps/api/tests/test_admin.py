"""관리자(Admin) 엔드포인트 E2E 테스트.

커버리지:
  POST   /admin/auth/login
  POST   /admin/auth/change-password
  GET    /admin/auth/me
  GET    /admin/members
  POST   /admin/members
  GET    /admin/members/{id}
  PATCH  /admin/members/{id}/status
  POST   /admin/members/{id}/points/adjust
  GET    /admin/modules
  POST   /admin/modules
  PATCH  /admin/modules/{id}
  DELETE /admin/modules/{id}
  GET    /admin/audit-logs
  GET    /admin/settings/log-retention
  PUT    /admin/settings/log-retention
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 관리자 인증
# ---------------------------------------------------------------------------


def test_admin_login_success(client: TestClient):
    """기본 admin/1234 로그인 → 200 + must_change_password=True."""
    resp = client.post("/admin/auth/login", json={"admin_id": "admin", "password": "1234"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["must_change_password"] is True
    assert body["role"] == "super_admin"


def test_admin_login_wrong_password(client: TestClient):
    """잘못된 비밀번호 → 401."""
    resp = client.post("/admin/auth/login", json={"admin_id": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_admin_login_unknown_id(client: TestClient):
    """미등록 admin_id → 401."""
    resp = client.post("/admin/auth/login", json={"admin_id": "ghost", "password": "1234"})
    assert resp.status_code == 401


def test_admin_get_me(client: TestClient, admin_headers: dict):
    """GET /admin/auth/me → 200 + 관리자 정보."""
    resp = client.get("/admin/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["admin_id"] == "admin"
    assert body["role"] == "super_admin"
    assert body["is_active"] is True


def test_admin_change_password(client: TestClient, admin_headers: dict):
    """비밀번호 변경 → 200 {"status": "ok"}."""
    resp = client.post(
        "/admin/auth/change-password",
        json={"current_password": "1234", "new_password": "newpass123"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_admin_change_password_wrong_current(client: TestClient, admin_headers: dict):
    """현재 비밀번호 불일치 → 400."""
    resp = client.post(
        "/admin/auth/change-password",
        json={"current_password": "wrongcurrent", "new_password": "newpass123"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_admin_change_password_same(client: TestClient, admin_headers: dict):
    """동일한 비밀번호로 변경 → 400."""
    resp = client.post(
        "/admin/auth/change-password",
        json={"current_password": "1234", "new_password": "1234"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_admin_change_password_too_short(client: TestClient, admin_headers: dict):
    """8자 미만 새 비밀번호 → 400."""
    resp = client.post(
        "/admin/auth/change-password",
        json={"current_password": "1234", "new_password": "abc"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_admin_me_requires_auth(client: TestClient):
    """토큰 없이 /admin/auth/me → 401."""
    resp = client.get("/admin/auth/me")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 회원 관리
# ---------------------------------------------------------------------------


def test_admin_list_members_empty(client: TestClient, admin_headers: dict):
    """회원 없을 때 빈 배열."""
    resp = client.get("/admin/members", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_create_member(client: TestClient, admin_headers: dict):
    """관리자가 회원 생성 → 201 + id/email."""
    resp = client.post(
        "/admin/members",
        json={"email": "member@example.com", "password": "member123", "initial_points": 100},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["email"] == "member@example.com"


def test_admin_create_member_duplicate_email(client: TestClient, admin_headers: dict):
    """중복 이메일로 생성 → 409."""
    payload = {"email": "dup@example.com", "password": "pass1234"}
    client.post("/admin/members", json=payload, headers=admin_headers)
    resp = client.post("/admin/members", json=payload, headers=admin_headers)
    assert resp.status_code == 409


def test_admin_create_member_invalid_email(client: TestClient, admin_headers: dict):
    """유효하지 않은 이메일 → 400."""
    resp = client.post(
        "/admin/members",
        json={"email": "notanemail", "password": "pass1234"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_admin_create_member_short_password(client: TestClient, admin_headers: dict):
    """짧은 비밀번호 → 400."""
    resp = client.post(
        "/admin/members",
        json={"email": "valid@example.com", "password": "abc"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_admin_get_member_detail(client: TestClient, admin_headers: dict):
    """생성된 회원 상세 조회."""
    create_resp = client.post(
        "/admin/members",
        json={"email": "detail@example.com", "password": "detail123"},
        headers=admin_headers,
    )
    user_id = create_resp.json()["id"]

    resp = client.get(f"/admin/members/{user_id}", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "member" in body
    assert body["member"]["email"] == "detail@example.com"
    assert "keywords" in body
    assert "access_logs" in body
    assert "action_logs" in body


def test_admin_get_member_not_found(client: TestClient, admin_headers: dict):
    """없는 회원 조회 → 404."""
    fake_id = "00000000-0000-0000-0000-000000000099"
    resp = client.get(f"/admin/members/{fake_id}", headers=admin_headers)
    assert resp.status_code == 404


def test_admin_update_member_status(client: TestClient, admin_headers: dict):
    """회원 상태 변경 suspended → active."""
    create_resp = client.post(
        "/admin/members",
        json={"email": "status@example.com", "password": "status123"},
        headers=admin_headers,
    )
    user_id = create_resp.json()["id"]

    resp = client.patch(
        f"/admin/members/{user_id}/status",
        json={"status": "suspended", "reason": "규정 위반"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["member_status"] == "suspended"

    resp2 = client.patch(
        f"/admin/members/{user_id}/status",
        json={"status": "active"},
        headers=admin_headers,
    )
    assert resp2.json()["member_status"] == "active"


def test_admin_point_adjust_small(client: TestClient, admin_headers: dict):
    """10000 이하 포인트 즉시 적용."""
    create_resp = client.post(
        "/admin/members",
        json={"email": "points@example.com", "password": "points123"},
        headers=admin_headers,
    )
    user_id = create_resp.json()["id"]

    resp = client.post(
        f"/admin/members/{user_id}/points/adjust",
        json={"amount": 500, "reason": "이벤트 보상"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "applied"
    assert body["points"] == 500


def test_admin_members_requires_auth(client: TestClient):
    """토큰 없이 회원 관리 접근 → 401."""
    assert client.get("/admin/members").status_code == 401
    assert client.post("/admin/members", json={}).status_code == 401


# ---------------------------------------------------------------------------
# 서비스 모듈
# ---------------------------------------------------------------------------


def _create_module(client: TestClient, headers: dict, module_key: str = "test-module") -> dict:
    resp = client.post(
        "/admin/modules",
        json={
            "module_key": module_key,
            "name": "테스트 모듈",
            "route_path": "/test",
            "description": "E2E 테스트용",
            "is_active": True,
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_admin_list_modules_empty(client: TestClient, admin_headers: dict):
    """모듈 없을 때 빈 배열."""
    resp = client.get("/admin/modules", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_create_module(client: TestClient, admin_headers: dict):
    """모듈 생성 → 201 + id."""
    resp = client.post(
        "/admin/modules",
        json={"module_key": "new-mod", "name": "새 모듈", "route_path": "/new"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


def test_admin_create_module_duplicate_key(client: TestClient, admin_headers: dict):
    """중복 module_key → 409."""
    _create_module(client, admin_headers, "dup-key")
    resp = client.post(
        "/admin/modules",
        json={"module_key": "dup-key", "name": "중복", "route_path": "/dup"},
        headers=admin_headers,
    )
    assert resp.status_code == 409


def test_admin_update_module(client: TestClient, admin_headers: dict):
    """모듈 이름/설명 수정 → 200."""
    mod_id = _create_module(client, admin_headers, "update-mod")["id"]

    resp = client.patch(
        f"/admin/modules/{mod_id}",
        json={"name": "수정된 모듈", "is_active": False},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_admin_update_module_noop(client: TestClient, admin_headers: dict):
    """변경 없이 수정 → 200 {"status": "noop"}."""
    mod_id = _create_module(client, admin_headers, "noop-mod")["id"]

    # 동일 값으로 패치 → 서버가 noop 반환
    resp = client.patch(
        f"/admin/modules/{mod_id}",
        json={"name": "테스트 모듈"},  # 생성 시 이름과 동일
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "noop"


def test_admin_delete_module(client: TestClient, admin_headers: dict):
    """모듈 삭제 → 204."""
    mod_id = _create_module(client, admin_headers, "del-mod")["id"]
    resp = client.delete(f"/admin/modules/{mod_id}", headers=admin_headers)
    assert resp.status_code == 204


def test_admin_delete_module_not_found(client: TestClient, admin_headers: dict):
    """없는 모듈 삭제 → 404."""
    fake_id = "00000000-0000-0000-0000-000000000099"
    resp = client.delete(f"/admin/modules/{fake_id}", headers=admin_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 감사 로그
# ---------------------------------------------------------------------------


def test_admin_audit_logs(client: TestClient, admin_headers: dict):
    """감사 로그 조회 → 200 + 목록 (관리자 생성 작업 포함)."""
    # 회원 생성 → 감사 로그 발생
    client.post(
        "/admin/members",
        json={"email": "audit@example.com", "password": "audit1234"},
        headers=admin_headers,
    )
    resp = client.get("/admin/audit-logs", headers=admin_headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
    # 최신 로그가 member_create 액션임을 확인
    action_types = [l["action_type"] for l in logs]
    assert "member_create" in action_types


def test_admin_audit_logs_requires_auth(client: TestClient):
    """토큰 없이 감사 로그 → 401."""
    assert client.get("/admin/audit-logs").status_code == 401


# ---------------------------------------------------------------------------
# 앱 설정 (로그 보존 정책)
# ---------------------------------------------------------------------------


def test_admin_get_log_retention_default(client: TestClient, admin_headers: dict):
    """기본 로그 보존 정책 → permanent."""
    resp = client.get("/admin/settings/log-retention", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"] == "log_retention"
    assert body["value"] == "permanent"


def test_admin_update_log_retention(client: TestClient, admin_headers: dict):
    """로그 보존 정책 변경 → 200 반영."""
    resp = client.put(
        "/admin/settings/log-retention",
        json={"value": "days:30"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["value"] == "days:30"

    resp2 = client.get("/admin/settings/log-retention", headers=admin_headers)
    assert resp2.json()["value"] == "days:30"


def test_admin_update_log_retention_invalid(client: TestClient, admin_headers: dict):
    """잘못된 보존 정책 값 → 400."""
    resp = client.put(
        "/admin/settings/log-retention",
        json={"value": "weekly"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_admin_update_log_retention_zero_days(client: TestClient, admin_headers: dict):
    """days:0 → 400."""
    resp = client.put(
        "/admin/settings/log-retention",
        json={"value": "days:0"},
        headers=admin_headers,
    )
    assert resp.status_code == 400
