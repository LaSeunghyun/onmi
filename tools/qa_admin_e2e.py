from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def _expect(name: str, cond: bool, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=cond, detail=detail)


def run() -> int:
    client = TestClient(app)
    now_tag = datetime.now().strftime("%Y%m%d%H%M%S")
    checks: list[CheckResult] = []

    # 1) admin login fail (wrong password)
    bad_admin_login = client.post("/admin/auth/login", json={"admin_id": "admin", "password": "wrong-password"})
    checks.append(
        _expect(
            "admin_login_rejects_wrong_password",
            bad_admin_login.status_code == 401,
            f"status={bad_admin_login.status_code}",
        )
    )

    # 2) admin login
    admin_login = client.post("/admin/auth/login", json={"admin_id": "admin", "password": "1234"})
    checks.append(_expect("admin_login", admin_login.status_code == 200, f"status={admin_login.status_code}"))
    if admin_login.status_code != 200:
        _print(checks)
        return 1
    admin_token = admin_login.json()["access_token"]
    admin_h = {"Authorization": f"Bearer {admin_token}"}

    # 3) unauthorized admin path
    unauth_members = client.get("/admin/members")
    checks.append(_expect("admin_members_requires_token", unauth_members.status_code == 401, f"status={unauth_members.status_code}"))

    # 4) create member from admin
    email = f"qa-member-{now_tag}@example.com"
    create_member = client.post(
        "/admin/members",
        headers=admin_h,
        json={"email": email, "password": "password123", "status": "active", "initial_points": 100},
    )
    checks.append(_expect("admin_create_member", create_member.status_code == 201, f"status={create_member.status_code}"))
    if create_member.status_code != 201:
        _print(checks)
        return 1
    member_id = create_member.json()["id"]

    # 5) duplicate member email should fail
    duplicate_member = client.post(
        "/admin/members",
        headers=admin_h,
        json={"email": email, "password": "password123", "status": "active", "initial_points": 0},
    )
    checks.append(
        _expect(
            "admin_create_member_duplicate_email_rejected",
            duplicate_member.status_code == 409,
            f"status={duplicate_member.status_code}",
        )
    )

    # 6) app login with admin-created member
    app_login = client.post("/auth/login", json={"email": email, "password": "password123"})
    checks.append(_expect("member_login_in_app", app_login.status_code == 200, f"status={app_login.status_code}"))
    if app_login.status_code != 200:
        _print(checks)
        return 1
    member_token = app_login.json()["access_token"]
    member_h = {"Authorization": f"Bearer {member_token}"}

    # 7) app login fail (wrong password)
    bad_member_login = client.post("/auth/login", json={"email": email, "password": "wrong-password"})
    checks.append(
        _expect(
            "member_login_rejects_wrong_password",
            bad_member_login.status_code == 401,
            f"status={bad_member_login.status_code}",
        )
    )

    # 8) member token must not access admin APIs
    member_token_on_admin = client.get("/admin/members", headers=member_h)
    checks.append(
        _expect(
            "member_token_rejected_on_admin_api",
            member_token_on_admin.status_code == 401,
            f"status={member_token_on_admin.status_code}",
        )
    )

    # 9) member behavior logs via keyword flow
    kw_create = client.post("/keywords", headers=member_h, json={"text": f"qa-keyword-{now_tag}", "is_active": True})
    checks.append(_expect("keyword_create", kw_create.status_code == 201, f"status={kw_create.status_code}"))

    # 10) admin detail should include access/action logs
    detail = client.get(f"/admin/members/{member_id}", headers=admin_h)
    has_logs = False
    if detail.status_code == 200:
        body = detail.json()
        has_logs = isinstance(body.get("access_logs"), list) and isinstance(body.get("action_logs"), list)
    checks.append(_expect("admin_member_detail_logs", detail.status_code == 200 and has_logs, f"status={detail.status_code}, has_logs={has_logs}"))

    # 11) module create/list
    module_key = f"qa-module-{now_tag}"
    module_create = client.post(
        "/admin/modules",
        headers=admin_h,
        json={
            "module_key": module_key,
            "name": "QA Module",
            "route_path": f"/admin/modules/{module_key}",
            "description": "qa",
            "is_active": True,
        },
    )
    checks.append(_expect("module_create", module_create.status_code == 201, f"status={module_create.status_code}"))
    module_list = client.get("/admin/modules", headers=admin_h)
    module_found = False
    if module_list.status_code == 200:
        module_found = any(m.get("module_key") == module_key for m in module_list.json())
    checks.append(_expect("module_list_contains_new", module_list.status_code == 200 and module_found, f"status={module_list.status_code}, found={module_found}"))

    # 12) duplicate module key should fail
    duplicate_module = client.post(
        "/admin/modules",
        headers=admin_h,
        json={
            "module_key": module_key,
            "name": "QA Module Duplicate",
            "route_path": f"/admin/modules/{module_key}-dup",
            "description": "qa-dup",
            "is_active": True,
        },
    )
    checks.append(
        _expect(
            "module_create_duplicate_key_rejected",
            duplicate_module.status_code == 409,
            f"status={duplicate_module.status_code}",
        )
    )

    # 13) log retention setting update
    retention_put = client.put("/admin/settings/log-retention", headers=admin_h, json={"value": "days:365"})
    retention_ok = retention_put.status_code == 200 and retention_put.json().get("value") == "days:365"
    checks.append(_expect("log_retention_update", retention_ok, f"status={retention_put.status_code}"))

    # 14) invalid log retention format should fail
    invalid_retention_put = client.put("/admin/settings/log-retention", headers=admin_h, json={"value": "days:0"})
    checks.append(
        _expect(
            "log_retention_invalid_value_rejected",
            invalid_retention_put.status_code == 400,
            f"status={invalid_retention_put.status_code}",
        )
    )

    # 15) point policy: auto apply under 10000
    point_adjust = client.post(
        f"/admin/members/{member_id}/points/adjust",
        headers=admin_h,
        json={"amount": 5000, "reason": "qa-auto"},
    )
    auto_applied = point_adjust.status_code == 200 and point_adjust.json().get("status") == "applied"
    checks.append(_expect("point_auto_apply_under_threshold", auto_applied, f"status={point_adjust.status_code}"))

    # 16) point single adjustment limit over threshold should fail
    point_adjust_over_limit = client.post(
        f"/admin/members/{member_id}/points/adjust",
        headers=admin_h,
        json={"amount": 100001, "reason": "qa-over-limit"},
    )
    checks.append(
        _expect(
            "point_adjust_over_single_limit_rejected",
            point_adjust_over_limit.status_code == 400,
            f"status={point_adjust_over_limit.status_code}",
        )
    )

    # 17) audit log should have records
    audit_list = client.get("/admin/audit-logs", headers=admin_h)
    audit_ok = audit_list.status_code == 200 and len(audit_list.json()) > 0
    checks.append(_expect("audit_log_exists", audit_ok, f"status={audit_list.status_code}, count={len(audit_list.json()) if audit_list.status_code == 200 else 0}"))

    _print(checks)
    return 0 if all(c.ok for c in checks) else 1


def _print(checks: list[CheckResult]) -> None:
    print("=== QA ADMIN E2E RESULT ===")
    for c in checks:
        status = "PASS" if c.ok else "FAIL"
        print(f"[{status}] {c.name} - {c.detail}")
    passed = sum(1 for c in checks if c.ok)
    print(f"Summary: {passed}/{len(checks)} passed")


if __name__ == "__main__":
    raise SystemExit(run())
