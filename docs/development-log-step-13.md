# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 13
- **Goal**: 일일 리포트 알림(설정/권한/예약/딥링크)을 구현한다.

## Completed implementations (this step)

### API

- 알림 설정 저장/조회 엔드포인트 추가
  - `GET /settings/notification` (기본값 09:00, enabled=true)
  - `PUT /settings/notification` (HH:MM 검증)
- `NotificationSetting` 모델 추가(유저당 1개)

### Mobile

- `expo-notifications` 기반 로컬 알림
  - 권한 요청
  - 매일 반복 알림 예약/취소(예약 ID는 secure store 저장)
  - 알림 탭 시 `리포트` 탭으로 이동 + 날짜를 “오늘”로 맞춤(딥링크 동작)
- 설정 화면(modal) 확장
  - 알림 사용 토글, 시간(HH:MM) 입력, 저장
  - 로그아웃 유지

### 검증

- API 스모크 테스트
  - 기본 설정 조회 및 PUT 업데이트 확인
- 모바일 타입체크 통과

## Files modified

- `/apps/api/app/models.py`
- `/apps/api/app/routers/settings.py`
- `/apps/api/app/main.py`
- `/apps/mobile/lib/notifications.ts`
- `/apps/mobile/lib/settings.ts`
- `/apps/mobile/lib/auth.tsx`
- `/apps/mobile/app/_layout.tsx`
- `/apps/mobile/app/(tabs)/index.tsx`
- `/apps/mobile/app/modal.tsx`

## What is currently stable

- 사용자가 알림 시간/사용 여부를 저장할 수 있고, 모바일에서 매일 반복 알림을 예약/취소할 수 있다.
- 알림을 탭하면 앱이 열리면서 리포트 탭으로 이동한다.

## What remains

- Step 13 완료 처리(상태 반영): `python tools/devlog.py complete 13`

## Exact next implementation boundary

- **Boundary**: MVP 완료. (Step 14 운영/분석/피드백은 선택)
- **Completion criteria**:
  - 사용자 관점 핵심 플로우(로그인 → 키워드 → 리포트 생성/조회 → 알림) 동작

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-13.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.

