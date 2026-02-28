# Admin 도메인

서비스 운영 관리와 감사 기록을 담당하는 도메인.

---

## 역할

- 관리자 계정 인증 (admin_id + password)
- 멤버 상태 관리 (정지/복구)
- 포인트 조정 요청·승인·적용
- 관리자 행동 감사 로그 기록
- 앱 전역 설정 키-값 관리
- 서비스 모듈 등록·활성화 관리

---

## 모델

### `AdminUser`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `admin_id` | str (unique, index) | 로그인 ID (기본값 `"admin"`) |
| `password_hash` | str | bcrypt 해시 |
| `role` | str | `super_admin` (현재 단일 역할) |
| `must_change_password` | bool | 초기 비밀번호 변경 강제 여부. 기본 `true` |
| `is_active` | bool | 계정 활성 여부. 기본 `true` |
| `created_at` | datetime | |
| `updated_at` | datetime | |

> 앱 기동 시 `AdminService.ensure_default_admin`으로 초기 계정(`admin`/`1234`) 자동 생성.
> **최초 로그인 후 반드시 비밀번호 변경 필요.**

### `ServiceModule`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `module_key` | str (unique, index) | 모듈 식별자 |
| `name` | str | 표시 이름 |
| `route_path` | str | 연결 라우트 경로 |
| `description` | str? | 설명 |
| `is_active` | bool | 모듈 활성 여부. 기본 `true` |
| `created_at` | datetime | |
| `updated_at` | datetime | |

### `AdminAuditLog`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `admin_user_id` | UUID (FK → AdminUser) | 행위 관리자 |
| `action_type` | str | 수행한 액션 종류 |
| `target_type` | str | 대상 엔티티 종류 |
| `target_id` | UUID? | 대상 엔티티 ID |
| `reason` | str? | 처리 사유 |
| `before_json` | str? | 변경 전 상태 (JSON) |
| `after_json` | str? | 변경 후 상태 (JSON) |
| `created_at` | datetime | |

### `AppSetting`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `key` | str (unique, index) | 설정 키 |
| `value` | str | 설정 값 |
| `updated_at` | datetime | |

### `PointAdjustmentRequest`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `member_user_id` | UUID (FK → User) | 대상 멤버 |
| `amount` | int | 조정 포인트 (양수=추가, 음수=차감) |
| `reason` | str | 조정 사유 |
| `requested_by_admin_id` | UUID (FK → AdminUser) | 요청 관리자 |
| `approved_by_admin_id` | UUID? (FK → AdminUser) | 승인 관리자 |
| `status` | str | `requested` \| `approved` \| `rejected` \| `applied` |
| `created_at` | datetime | |
| `updated_at` | datetime | |

---

## 서비스 (`AdminService`)

| 메서드 | 설명 |
|--------|------|
| `ensure_default_admin` | `admin_id="admin"` 계정 없으면 기본 계정 생성 (`1234`, `must_change_password=true`) |
| `write_audit_log` | 관리자 행동 감사 기록. `before_obj`/`after_obj`는 JSON으로 직렬화 |
| `get_setting` | 키로 설정값 조회. 없으면 `default_value`로 자동 생성 후 반환 |
| `set_setting` | 키-값 저장 (없으면 INSERT, 있으면 UPDATE) |

---

## API 엔드포인트

### 인증
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/admin/auth/login` | 관리자 로그인 → JWT 반환 |

### 대시보드·멤버
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/admin/dashboard` | KPI 지표 (가입자 수, 활성 유저, 키워드 수 등) |
| GET | `/admin/members` | 멤버 목록 (검색·필터·페이지네이션) |
| GET | `/admin/members/{id}` | 멤버 상세 |
| PATCH | `/admin/members/{id}/status` | 멤버 상태 변경 (active/suspended) |
| GET | `/admin/audit-logs` | 감사 로그 목록 |

### 포인트
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/admin/point-adjustments` | 포인트 조정 요청 생성 |
| PATCH | `/admin/point-adjustments/{id}` | 요청 승인/거절 |

### 설정
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/admin/settings` | 앱 설정 목록 |
| PUT | `/admin/settings/{key}` | 설정값 변경 |

---

## 주요 규칙

- 기본 계정 비밀번호(`1234`)는 최초 로그인 후 즉시 변경 필요 (`must_change_password=true`)
- 모든 관리자 행동은 `AdminAuditLog`에 `before_json` / `after_json` 포함해 기록
- `AppSetting`은 키-값 형태의 단순 전역 설정 저장소 (e.g. 기능 플래그)
- 포인트 조정은 요청(`requested`) → 승인(`approved`) → 적용(`applied`) 흐름. 단계별 다른 관리자가 승인 가능
- Identity 도메인의 `MemberActionLog`(유저 행동)와 다름 — `AdminAuditLog`는 관리자 행동 전용

---

## 파일 위치

```
apps/api/app/domains/admin/
├── models.py    # AdminUser, ServiceModule, AdminAuditLog, AppSetting, PointAdjustmentRequest
├── service.py   # AdminService
└── schemas.py   # 요청/응답 Pydantic 스키마
apps/api/app/routers/
├── admin.py         # 대시보드, 멤버, 포인트, 설정
└── admin_auth.py    # 관리자 인증
```
