# Project: touch (어드민 웹 UI)

## Current step

- **Step number**: 15
- **Goal**: 어드민 웹 UI(로그인/회원/모듈/감사로그)와 앱 로그인 연동 확인 경로를 구현한다.

## Completed implementations (this step)

### Mobile(Web) - 어드민 화면 추가

- `/admin/login`: 관리자 로그인 화면
- `/admin/dashboard`: 관리자 정보 및 비밀번호 변경 화면
- `/admin/members`: 회원 생성/조회/상태변경 화면
- `/admin/modules`: 모듈 생성/조회 화면
- `/admin/audit`: 감사로그 조회 화면

### 공통 인증 흐름

- `AdminAuthProvider` 추가
  - 어드민 토큰 저장(`SecureStore`)
  - 관리자 프로필 조회/로그아웃/비밀번호 변경 지원
- 루트 라우팅 가드 확장
  - `/admin/*` 경로는 일반 사용자 로그인 가드와 분리
  - 어드민 미인증 시 `/admin/login`으로 리다이렉트

### API 연동 보강 (UI 요구 충족)

- `POST /admin/members` 추가
  - 어드민에서 회원 계정을 생성
  - 생성 계정은 `User` 테이블 기반으로 앱 로그인 가능

## Files modified

- `/apps/mobile/app/_layout.tsx`
- `/apps/mobile/app/(auth)/login.tsx`
- `/apps/mobile/app/admin/_layout.tsx` (new)
- `/apps/mobile/app/admin/login.tsx` (new)
- `/apps/mobile/app/admin/dashboard.tsx` (new)
- `/apps/mobile/app/admin/members.tsx` (new)
- `/apps/mobile/app/admin/modules.tsx` (new)
- `/apps/mobile/app/admin/audit.tsx` (new)
- `/apps/mobile/lib/admin.ts` (new)
- `/apps/mobile/lib/adminAuth.tsx` (new)
- `/apps/api/app/routers/admin.py`

## What is currently stable

- 어드민 웹 UI 핵심 화면과 메뉴 이동이 동작한다.
- 어드민에서 회원을 생성하면 앱의 일반 로그인 API(`/auth/login`)로 로그인 가능하다.
- 모바일 타입체크(`npx tsc --noEmit`)가 통과한다.

## What remains

- Step 15 완료 처리(상태 반영): `python tools/devlog.py complete 15`
- Step 16에서 통합 QA/운영 안정화 진행

## Exact next implementation boundary

- **Boundary**: Step 16 - 어드민 통합 QA/운영 안정화
- **Completion criteria**:
  - 어드민/앱 연동 핵심 시나리오 체크리스트 통과
  - 권한/보안/로그 정책 테스트 결과 문서화

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-15.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.
