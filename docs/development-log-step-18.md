# Project: touch (디자인 시스템 컴포넌트화 2차)

## Current step

- **Step number**: 18
- **Goal**: 공통 UI 컴포넌트(Button/Input/Card)로 중복 스타일을 제거하고 접근성 포커스 기준을 강화한다.

## Completed implementations (this step)

### Component layer

- 공통 UI 컴포넌트 추가
  - `apps/mobile/components/ui/Button.tsx`
  - `apps/mobile/components/ui/Input.tsx`
  - `apps/mobile/components/ui/Card.tsx`
  - `apps/mobile/components/ui/index.ts`
- 공통 정책 반영
  - Button variant(`primary|secondary|danger`) + size(`md|lg`)
  - Input focus/error 상태 시각화
  - Card 표면/경계/간격 일원화

### Screen migration

- 어드민 화면 치환
  - `app/admin/login.tsx`
  - `app/admin/dashboard.tsx`
  - `app/admin/members.tsx`
  - `app/admin/modules.tsx`
  - `app/admin/audit.tsx`
- 사용자 인증/설정 화면 치환
  - `app/(auth)/login.tsx`
  - `app/(auth)/signup.tsx`
  - `app/modal.tsx`

### Token extension

- 다크모드 대응 semantic alias 추가
  - `apps/mobile/theme/tokens.ts`
  - `semantic.light`, `semantic.dark` 도입

### Validation

- `apps/mobile`: `npx tsc --noEmit` 통과
- 편집 파일 lint diagnostics 오류 없음

## Files modified

- `/apps/mobile/components/ui/Button.tsx` (new)
- `/apps/mobile/components/ui/Input.tsx` (new)
- `/apps/mobile/components/ui/Card.tsx` (new)
- `/apps/mobile/components/ui/index.ts` (new)
- `/apps/mobile/theme/tokens.ts`
- `/apps/mobile/app/admin/login.tsx`
- `/apps/mobile/app/admin/dashboard.tsx`
- `/apps/mobile/app/admin/members.tsx`
- `/apps/mobile/app/admin/modules.tsx`
- `/apps/mobile/app/admin/audit.tsx`
- `/apps/mobile/app/(auth)/login.tsx`
- `/apps/mobile/app/(auth)/signup.tsx`
- `/apps/mobile/app/modal.tsx`

## What is currently stable

- 버튼/입력/카드의 시각 및 상호작용 기준이 공통 컴포넌트로 고정되었다.
- 어드민/인증/설정 핵심 화면에서 중복 스타일 정의를 제거했다.

## What remains

- Step 18 완료 처리(상태 반영): `python tools/devlog.py complete 18`
- (선택) 리포트/키워드/상세 화면까지 컴포넌트 치환 확대

## Exact next implementation boundary

- **Boundary**: 디자인 시스템 3차 적용(전체 화면 컴포넌트 전면화)
- **Completion criteria**:
  - `app/(tabs)/index.tsx`, `app/(tabs)/two.tsx`, `app/article/[articleId].tsx`에 Button/Input/Card 적용
  - focus-visible 규칙을 링크/탭 네비게이션까지 확대

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-18.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.
