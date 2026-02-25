"""헬스체크 엔드포인트 E2E 테스트."""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """GET /health → 200 {"status": "ok"}"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
