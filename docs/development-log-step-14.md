# Project: touch (어드민 구축)

## Current step

- **Step number**: 14
- **Goal**: 어드민 백엔드 기반(API/권한/감사로그/정책)을 구현한다.

## Completed implementations (this step)

### API - Admin 인증/권한

- `POST /admin/auth/login`
  - 초기 계정 `admin/1234` 자동 부트스트랩
  - 관리자 전용 JWT(`typ=admin`) 발급
- `POST /admin/auth/change-password`
  - 관리자 비밀번호 변경(최소 길이 검증)
  - 변경 감사로그 기록
- `GET /admin/auth/me`
  - 관리자 계정/역할/비밀번호 변경 필요 여부 조회

### API - 회원 관리/행동 이력

- `GET /admin/members`
  - 회원 목록 조회 + 상태/포인트 표시
- `GET /admin/members/{user_id}`
  - 회원 상세 + 키워드 + 접속 로그 + 행동 로그 조회
- `PATCH /admin/members/{user_id}/status`
  - 회원 상태 변경(active/suspended) + 감사로그
- `POST /admin/members/{user_id}/points/adjust`
  - 포인트 조정 요청(사유 필수, 1회 한도 100000)
  - 10000 이하 자동 적용, 초과는 승인 대기
- `POST /admin/point-adjustments/{request_id}/approve`
  - 요청자와 다른 관리자가 승인/반영

### API - 모듈 관리/감사로그/설정

- `GET/POST/PATCH/DELETE /admin/modules`
  - 서비스 모듈 엔티티 CRUD
- `GET /admin/audit-logs`
  - 관리자 변경 이력 조회
- `GET/PUT /admin/settings/log-retention`
  - 기본값 `permanent`, `days:<n>` 정책 변경 지원

### 로그 수집 기반

- 회원 로그인 성공 시 접속 로그 저장
- 키워드 생성/수정/삭제 시 행동 로그 저장
- 관리자 주요 변경 작업에 감사로그 저장

## Files modified

- `/apps/api/app/main.py`
- `/apps/api/app/models.py`
- `/apps/api/app/security.py`
- `/apps/api/app/routers/auth.py`
- `/apps/api/app/routers/keywords.py`
- `/apps/api/app/admin_ops.py` (new)
- `/apps/api/app/deps_admin.py` (new)
- `/apps/api/app/routers/admin_auth.py` (new)
- `/apps/api/app/routers/admin.py` (new)

## What is currently stable

- 어드민 핵심 백엔드 API가 로컬에서 호출 가능하다.
- 초기 관리자 계정 로그인과 관리자 토큰 기반 접근 제어가 동작한다.
- 회원/모듈/감사로그/보존정책 관리 API 기본 플로우가 동작한다.

## What remains

- Step 14 완료 처리(상태 반영): `python tools/devlog.py complete 14`
- Step 15에서 어드민 웹 UI(로그인/회원/모듈/감사로그) 구현 및 QA 진행

## Exact next implementation boundary

- **Boundary**: Step 15 - 어드민 웹 UI 구축
- **Completion criteria**:
  - 운영자 로그인 및 권한별 메뉴 노출
  - 회원 관리/모듈 CRUD/감사로그 화면 구현
  - API 미연동 시 Mock 전환 가능

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-14.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.
