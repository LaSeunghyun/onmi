# Project: touch (어드민 UI 전반 점검)

## Current step

- **Step number**: 20
- **Goal**: 어드민 화면 전반의 로딩/빈 상태, 접근성(a11y), 레이아웃·간격을 보완한다.

## Completed implementations (this step)

### Layout & accessibility (_layout.tsx)

- 상단 검색 입력에 `accessibilityLabel="검색"` 추가
- 알림·프로필 영역에 `accessibilityLabel` 추가
- 로그아웃 버튼에 `accessibilityLabel="로그아웃"`, `accessibilityRole="button"` 추가
- 본문 영역에 `minHeight: 400` 적용해 콘텐츠 영역 최소 높이 보장

### Dashboard (dashboard.tsx)

- KPI 로딩 상태 추가: `loading` 상태에서 `ActivityIndicator` + "데이터 불러오는 중..." 표시
- 페이지 제목 스타일명을 `title` → `pageTitle`로 통일

### Members / Modules / Audit (members.tsx, modules.tsx, audit.tsx)

- 목록 로딩 시 `ActivityIndicator` + 안내 문구 표시
- 목록이 0건일 때 빈 상태 문구 표시
  - 회원: "등록된 회원이 없습니다. 위 폼에서 회원을 추가해 보세요."
  - 모듈: "등록된 모듈이 없습니다. 위 폼에서 모듈을 추가해 보세요."
  - 로그: "활동 로그가 없습니다."
- 회원 검색 Input에 `accessibilityLabel="회원 검색 이메일"` 추가

### Login (login.tsx)

- 관리자 ID / 비밀번호 Input에 `accessibilityLabel` 추가
- 로그인 오류 메시지에 `accessibilityLiveRegion="polite"` 추가 (스크린 리더 안내)
- 라벨·제목에 `space` 토큰으로 여백 통일

### Settings (settings.tsx)

- 프로필/보안 Input에 `accessibilityLabel` 추가
- 보안 설정 오류 메시지에 `accessibilityLiveRegion="polite"` 추가
- 섹션 제목·입력란 사이 `inputSpacing`(marginBottom) 적용

## Files modified

- `apps/mobile/app/admin/_layout.tsx`
- `apps/mobile/app/admin/dashboard.tsx`
- `apps/mobile/app/admin/members.tsx`
- `apps/mobile/app/admin/modules.tsx`
- `apps/mobile/app/admin/audit.tsx`
- `apps/mobile/app/admin/login.tsx`
- `apps/mobile/app/admin/settings.tsx`

## What is currently stable

- 어드민 모든 목록 화면에 로딩·빈 상태가 일관되게 표시된다.
- 로그인/설정/레이아웃 주요 요소에 접근성 레이블·역할이 부여되었다.
- 대시보드 제목 스타일이 다른 어드민 페이지와 동일한 `pageTitle`로 통일되었다.

## What remains

- (선택) 하드코딩 색상(`#1E293B`, `#64748B`)을 `theme/tokens`로 치환
- (선택) 에러 메시지를 상단 배너 등 고정 위치로 통일

## Exact next implementation boundary

- **Boundary**: 없음. 본 단계는 "전체 UI 점검" 요청에 대한 구현 완료.
- 다음 작업이 생기면 새 스텝으로 진행.

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

`/docs/development-log-step-20.md`를 읽고, 필요 시 "What remains" 항목만 선택 적용한다.
