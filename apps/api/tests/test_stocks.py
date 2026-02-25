"""주식 감시종목·신호 규칙·시그널 대시보드 E2E 테스트.

커버리지:
  GET    /stocks/search
  GET    /stocks/watchlist
  POST   /stocks/watchlist
  DELETE /stocks/watchlist/{id}
  PATCH  /stocks/watchlist/reorder
  PATCH  /stocks/watchlist/{id}/favorite
  GET    /stocks/rules
  PUT    /stocks/rules
  GET    /stocks/signals
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _add_watch(client: TestClient, headers: dict, corp_code: str = "00126380", srtn_cd: str = "005930", itms_nm: str = "삼성전자") -> dict:
    resp = client.post(
        "/stocks/watchlist",
        json={"corp_code": corp_code, "srtn_cd": srtn_cd, "itms_nm": itms_nm},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 종목 검색
# ---------------------------------------------------------------------------


def test_corp_search_empty_cache(client: TestClient, auth_headers: dict):
    """캐시 없을 때 검색 → 200 빈 배열."""
    resp = client.get("/stocks/search?q=삼성", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_corp_search_requires_auth(client: TestClient):
    """토큰 없이 검색 → 401."""
    resp = client.get("/stocks/search?q=카카오")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 감시종목 CRUD
# ---------------------------------------------------------------------------


def test_list_watchlist_empty(client: TestClient, auth_headers: dict):
    """감시종목 없을 때 빈 배열."""
    resp = client.get("/stocks/watchlist", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_watch_item(client: TestClient, auth_headers: dict):
    """감시종목 추가 → 201 + 필드 검증."""
    item = _add_watch(client, auth_headers)
    assert item["corp_code"] == "00126380"
    assert item["srtn_cd"] == "005930"
    assert item["itms_nm"] == "삼성전자"
    assert item["is_favorite"] is False
    assert "id" in item
    assert "sort_order" in item


def test_list_watchlist_after_create(client: TestClient, auth_headers: dict):
    """추가 후 목록에 표시."""
    _add_watch(client, auth_headers)
    resp = client.get("/stocks/watchlist", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_delete_watch_item(client: TestClient, auth_headers: dict):
    """감시종목 삭제 → 204 + 목록에서 제거."""
    item = _add_watch(client, auth_headers)
    resp = client.delete(f"/stocks/watchlist/{item['id']}", headers=auth_headers)
    assert resp.status_code == 204

    remaining = client.get("/stocks/watchlist", headers=auth_headers).json()
    assert all(w["id"] != item["id"] for w in remaining)


def test_toggle_favorite(client: TestClient, auth_headers: dict):
    """즐겨찾기 토글 → is_favorite 변경."""
    item = _add_watch(client, auth_headers)
    resp = client.patch(f"/stocks/watchlist/{item['id']}/favorite", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True

    resp2 = client.patch(f"/stocks/watchlist/{item['id']}/favorite", headers=auth_headers)
    assert resp2.json()["is_favorite"] is False


def test_reorder_watchlist(client: TestClient, auth_headers: dict):
    """감시종목 순서 변경 → 200 + 재정렬된 목록."""
    item1 = _add_watch(client, auth_headers, corp_code="A", srtn_cd="000001", itms_nm="종목1")
    item2 = _add_watch(client, auth_headers, corp_code="B", srtn_cd="000002", itms_nm="종목2")

    resp = client.patch(
        "/stocks/watchlist/reorder",
        json={"ordered_ids": [item2["id"], item1["id"]]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    reordered = resp.json()
    assert reordered[0]["id"] == item2["id"]
    assert reordered[1]["id"] == item1["id"]


def test_watchlist_requires_auth(client: TestClient):
    """토큰 없이 감시종목 접근 → 401."""
    assert client.get("/stocks/watchlist").status_code == 401
    assert client.post("/stocks/watchlist", json={}).status_code == 401


# ---------------------------------------------------------------------------
# 신호 규칙
# ---------------------------------------------------------------------------


def test_get_signal_rules_default(client: TestClient, auth_headers: dict):
    """기본 신호 규칙 조회 → 200 + 필드 포함."""
    resp = client.get("/stocks/rules", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "stop_loss_pct" in body
    assert "take_profit_pct" in body
    assert "ema_slope_threshold" in body
    assert "volume_ratio_on" in body
    assert "volume_ratio_multiplier" in body
    assert "push_enabled" in body


def test_update_signal_rules(client: TestClient, auth_headers: dict):
    """신호 규칙 업데이트 → 200 + 변경값 반영."""
    resp = client.put(
        "/stocks/rules",
        json={
            "stop_loss_pct": 5.0,
            "take_profit_pct": 10.0,
            "ema_slope_threshold": 0.5,
            "volume_ratio_on": False,
            "volume_ratio_multiplier": 2.0,
            "push_enabled": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["stop_loss_pct"] == 5.0
    assert body["take_profit_pct"] == 10.0
    assert body["volume_ratio_on"] is False
    assert body["push_enabled"] is False


def test_signal_rules_requires_auth(client: TestClient):
    """토큰 없이 신호 규칙 접근 → 401."""
    assert client.get("/stocks/rules").status_code == 401
    assert client.put("/stocks/rules", json={}).status_code == 401


# ---------------------------------------------------------------------------
# 시그널 대시보드
# ---------------------------------------------------------------------------


def test_get_signals_empty_watchlist(client: TestClient, auth_headers: dict):
    """감시종목 없을 때 신호 조회 → 200 빈 배열."""
    resp = client.get("/stocks/signals", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_signals_with_watchlist(client: TestClient, auth_headers: dict):
    """감시종목 추가 후 신호 조회 → 200 항목 포함 (외부 API 미호출 환경)."""
    _add_watch(client, auth_headers)
    resp = client.get("/stocks/signals", headers=auth_headers)
    assert resp.status_code == 200
    # 외부 API 미설정 환경에서는 hold 신호 또는 빈 배열로 반환될 수 있음
    body = resp.json()
    assert isinstance(body, list)
    if body:
        first = body[0]
        assert "signal" in first
        assert first["signal"] in ("buy", "sell", "hold")
        assert "corp_code" in first
        assert "reasons" in first


def test_signals_requires_auth(client: TestClient):
    """토큰 없이 신호 조회 → 401."""
    assert client.get("/stocks/signals").status_code == 401
