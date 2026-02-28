# Identity 도메인

사용자 인증과 멤버 관리를 담당하는 도메인.

---

## 역할

- 회원가입 / 로그인 (이메일+패스워드 기반)
- JWT 액세스 토큰 발급
- 멤버 프로필 및 상태 관리
- 접속·행동 감사 로그 기록

---

## 모델

### `User`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | 자동 생성 |
| `email` | str (unique, index) | 소문자 정규화 후 저장 |
| `password_hash` | str | bcrypt 해시 |
| `auth_provider` | str | 기본값 `"email"` |
| `created_at` | datetime | 가입 시각 |
| `updated_at` | datetime | 수정 시각 |

### `MemberProfile`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User, unique) | 1:1 관계 |
| `status` | str | `active` \| `suspended` |
| `points` | int | 포인트 잔액 |
| `updated_at` | datetime | |

### `MemberAccessLog`
| 필드 | 타입 | 설명 |
|------|------|------|
| `user_id` | UUID (FK → User) | |
| `event_type` | str | `login_success` \| `login_fail` |
| `ip` | str? | 클라이언트 IP |
| `user_agent` | str? | |
| `created_at` | datetime | |

### `MemberActionLog`
| 필드 | 타입 | 설명 |
|------|------|------|
| `user_id` | UUID (FK → User) | |
| `action_type` | str | `keyword_create` \| `keyword_update` \| `keyword_delete` 등 |
| `entity_type` | str | 변경 대상 엔티티 종류 |
| `entity_id` | UUID? | 변경 대상 ID |
| `details_json` | str? | 상세 정보 (JSON 문자열) |
| `created_at` | datetime | |

---

## 서비스 (`UserService` / `MemberService`)

| 메서드 | 설명 |
|--------|------|
| `UserService.signup` | 이메일 중복 확인 → 패스워드 최소 8자 검증 → User 저장 → MemberProfile 자동 생성 → JWT 반환 |
| `UserService.authenticate` | 이메일·패스워드 검증 → MemberProfile upsert → JWT 반환 |
| `UserService.get_by_id` | user_id로 단건 조회 |
| `MemberService.ensure_profile` | MemberProfile 없으면 생성 (signup/login 양쪽에서 호출) |
| `MemberService.write_access_log` | 로그인 성공·실패 이벤트 기록 |
| `MemberService.write_action_log` | 키워드 CRUD 등 행동 감사 기록 |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/auth/signup` | 회원가입, `{ email, password }` → `{ access_token }` |
| POST | `/auth/login` | 로그인, `{ email, password }` → `{ access_token }` |
| GET | `/me` | 현재 로그인 유저 프로필 조회 |

---

## 주요 규칙

- 이메일은 `strip().lower()` 정규화 후 저장 — 대소문자 혼용 중복 방지
- 패스워드는 평문 저장 안 함 (bcrypt 해시)
- JWT는 `sub` 필드에 `user_id` (UUID 문자열) 포함
- `MemberProfile`은 회원가입·로그인 시 자동 보장 (`ensure_profile`)
- 포인트 조정은 Admin 도메인의 `PointAdjustmentRequest`를 통해서만 수행

---

## 파일 위치

```
apps/api/app/domains/identity/
├── models.py    # User, MemberProfile, MemberAccessLog, MemberActionLog
├── service.py   # UserService, MemberService
└── schemas.py   # 요청/응답 Pydantic 스키마
apps/api/app/routers/
├── auth.py      # signup, login
└── me.py        # 현재 유저 조회
```
