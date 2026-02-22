# Project: touch (앱/어드민 디자인 시스템 정렬)

## Current step

- **Step number**: 17
- **Goal**: 앱과 어드민 UI를 공통 토큰 기반 디자인 시스템으로 정렬한다.

## Completed implementations (this step)

### Design system foundation

- 공통 토큰 파일 추가
  - `apps/mobile/theme/tokens.ts`
  - color(primary/secondary/neutral/semantic), typography, spacing, radius, motion 정의
- 공통 UI 프리미티브 추가
  - `apps/mobile/theme/primitives.ts`
  - page/card/input/button 스타일 기준선 제공
- 기존 탭 색상 상수와 토큰 연결
  - `apps/mobile/constants/Colors.ts`

### UI migration (app + admin)

- 앱 화면 토큰 치환
  - 인증: `app/(auth)/login.tsx`, `app/(auth)/signup.tsx`
  - 리포트/키워드/상세/설정: `app/(tabs)/index.tsx`, `app/(tabs)/two.tsx`, `app/article/[articleId].tsx`, `app/modal.tsx`
- 어드민 화면 토큰 치환
  - `app/admin/_layout.tsx`, `app/admin/login.tsx`, `app/admin/dashboard.tsx`
  - `app/admin/members.tsx`, `app/admin/modules.tsx`, `app/admin/audit.tsx`

### Documentation

- 레퍼런스 기반 디자인 시스템 문서 추가
  - `docs/design-system-step-17.md`
  - Product context / references / token definitions / component standards / a11y / implementation guide 포함

### validation

- TypeScript check 통과
  - `apps/mobile`: `npx tsc --noEmit`
- 편집 파일 lint diagnostics 확인
  - 오류 없음

## Files modified

- `/apps/mobile/theme/tokens.ts` (new)
- `/apps/mobile/theme/primitives.ts` (new)
- `/apps/mobile/constants/Colors.ts`
- `/apps/mobile/app/(auth)/login.tsx`
- `/apps/mobile/app/(auth)/signup.tsx`
- `/apps/mobile/app/(tabs)/index.tsx`
- `/apps/mobile/app/(tabs)/two.tsx`
- `/apps/mobile/app/article/[articleId].tsx`
- `/apps/mobile/app/modal.tsx`
- `/apps/mobile/app/admin/_layout.tsx`
- `/apps/mobile/app/admin/login.tsx`
- `/apps/mobile/app/admin/dashboard.tsx`
- `/apps/mobile/app/admin/members.tsx`
- `/apps/mobile/app/admin/modules.tsx`
- `/apps/mobile/app/admin/audit.tsx`
- `/docs/design-system-step-17.md` (new)

## What is currently stable

- 앱/어드민의 핵심 화면이 단일 토큰 세트로 색상·간격·타이포 기준을 공유한다.
- 신규 화면 개발 시 `tokens + primitives`를 재사용할 수 있는 기준선이 생겼다.

## What remains

- Step 17 완료 처리(상태 반영): `python tools/devlog.py complete 17`
- (선택) 다크 모드 토큰 분기와 포커스 링 컴포넌트 레벨 표준화

## Exact next implementation boundary

- **Boundary**: 디자인 시스템 2차 확장(다크 모드 + 컴포넌트화)
- **Completion criteria**:
  - 공통 Button/Input/Card 컴포넌트 추출
  - 웹(어드민) focus-visible 규칙 강제
  - 다크 모드 semantic alias 도입

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-17.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.
