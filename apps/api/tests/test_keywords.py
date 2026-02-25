"""키워드(Keywords) 엔드포인트 E2E 테스트.

커버리지:
  GET    /keywords
  POST   /keywords
  PATCH  /keywords/{id}
  DELETE /keywords/{id}
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _create_keyword(client: TestClient, headers: dict, text: str = "삼성전자", is_active: bool = True) -> dict:
    resp = client.post("/keywords", json={"text": text, "is_active": is_active}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 목록 조회
# ---------------------------------------------------------------------------


def test_list_keywords_empty(client: TestClient, auth_headers: dict):
    """키워드 없을 때 빈 배열 반환."""
    resp = client.get("/keywords", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_keywords_after_create(client: TestClient, auth_headers: dict):
    """키워드 생성 후 목록에 나타남."""
    _create_keyword(client, auth_headers, "카카오")
    resp = client.get("/keywords", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["text"] == "카카오"


def test_list_keywords_status_filter(client: TestClient, auth_headers: dict):
    """status_filter 로 활성/비활성 필터링."""
    _create_keyword(client, auth_headers, "활성", is_active=True)
    _create_keyword(client, auth_headers, "비활성", is_active=False)

    resp_active = client.get("/keywords?status_filter=active", headers=auth_headers)
    assert resp_active.status_code == 200
    assert all(k["is_active"] for k in resp_active.json())

    resp_inactive = client.get("/keywords?status_filter=inactive", headers=auth_headers)
    assert resp_inactive.status_code == 200
    assert all(not k["is_active"] for k in resp_inactive.json())


def test_list_keywords_sort_alpha(client: TestClient, auth_headers: dict):
    """sort=alpha 로 정렬 시 오류 없이 반환."""
    _create_keyword(client, auth_headers, "네이버")
    _create_keyword(client, auth_headers, "구글")
    resp = client.get("/keywords?sort=alpha", headers=auth_headers)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 생성
# ---------------------------------------------------------------------------


def test_create_keyword_response_fields(client: TestClient, auth_headers: dict):
    """생성 응답에 필요한 필드가 모두 포함."""
    kw = _create_keyword(client, auth_headers, "LG에너지솔루션")
    assert "id" in kw
    assert kw["text"] == "LG에너지솔루션"
    assert kw["is_active"] is True
    assert kw["is_pinned"] is False
    assert "created_at" in kw
    assert "updated_at" in kw


def test_create_keyword_inactive(client: TestClient, auth_headers: dict):
    """is_active=False 로 생성 시 비활성 키워드 반환."""
    kw = _create_keyword(client, auth_headers, "하이닉스", is_active=False)
    assert kw["is_active"] is False


def test_create_keyword_requires_auth(client: TestClient):
    """토큰 없이 POST /keywords → 401."""
    resp = client.post("/keywords", json={"text": "test", "is_active": True})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 수정
# ---------------------------------------------------------------------------


def test_update_keyword_deactivate(client: TestClient, auth_headers: dict):
    """is_active=False 로 수정."""
    kw = _create_keyword(client, auth_headers, "현대차")
    resp = client.patch(f"/keywords/{kw['id']}", json={"is_active": False}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_update_keyword_pin(client: TestClient, auth_headers: dict):
    """is_pinned=True 로 핀 설정."""
    kw = _create_keyword(client, auth_headers, "포스코")
    resp = client.patch(f"/keywords/{kw['id']}", json={"is_pinned": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_pinned"] is True


def test_update_keyword_not_found(client: TestClient, auth_headers: dict):
    """존재하지 않는 키워드 수정 → 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.patch(f"/keywords/{fake_id}", json={"is_active": False}, headers=auth_headers)
    assert resp.status_code == 404


def test_update_keyword_requires_auth(client: TestClient, auth_headers: dict):
    """토큰 없이 PATCH → 401."""
    kw = _create_keyword(client, auth_headers, "SK하이닉스")
    resp = client.patch(f"/keywords/{kw['id']}", json={"is_active": False})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 삭제
# ---------------------------------------------------------------------------


def test_delete_keyword(client: TestClient, auth_headers: dict):
    """키워드 삭제 후 목록에서 사라짐."""
    kw = _create_keyword(client, auth_headers, "삭제대상")
    resp = client.delete(f"/keywords/{kw['id']}", headers=auth_headers)
    assert resp.status_code == 204

    items = client.get("/keywords", headers=auth_headers).json()
    assert all(k["id"] != kw["id"] for k in items)


def test_delete_keyword_not_found(client: TestClient, auth_headers: dict):
    """존재하지 않는 키워드 삭제 → 404."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = client.delete(f"/keywords/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_keyword_requires_auth(client: TestClient, auth_headers: dict):
    """토큰 없이 DELETE → 401."""
    kw = _create_keyword(client, auth_headers, "인증필요")
    resp = client.delete(f"/keywords/{kw['id']}")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 사용자 격리
# ---------------------------------------------------------------------------


def test_keywords_isolated_between_users(client: TestClient):
    """서로 다른 사용자는 각자의 키워드만 조회."""
    # 사용자 A
    tok_a = client.post("/auth/signup", json={"email": "a@test.com", "password": "passA1234"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {tok_a}"}
    client.post("/keywords", json={"text": "A키워드", "is_active": True}, headers=headers_a)

    # 사용자 B
    tok_b = client.post("/auth/signup", json={"email": "b@test.com", "password": "passB1234"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {tok_b}"}

    items_b = client.get("/keywords", headers=headers_b).json()
    assert items_b == []
