# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 12
- **Goal**: 리포트 UX(날짜/필터/상태/상세)를 API+모바일로 완성한다.

## Completed implementations (this step)

### API

- 리포트 조회 엔드포인트 추가
  - `GET /report?date_kst=YYYY-MM-DD&keyword_id=...`
  - 필터 칩용 키워드 카운트 포함
  - 아이템에 `summary_ko`, `sentiment`, `translation_status` 포함(ProcessingResult 조인)
- 기사 상세 엔드포인트 추가
  - `GET /articles/{article_id}`

### Mobile

- `리포트` 탭 구현(기본)
  - 날짜 전/후 이동(간단한 date selector)
  - “전체 + 키워드 칩” 필터
  - 요약 카드(키워드 수/이슈 수)
  - 기사 카드 리스트(키워드 배지, 감성, 요약, 번역 표시)
  - 로딩/빈/에러 상태 및 새로고침
- 기사 상세 화면 추가
  - 요약/감성/번역 안내 + 원문 링크

### 검증

- API에서 `collect → process → report` 호출로 `summary_ko`가 리포트 아이템에 포함되는 것 확인

## Files modified

- `/apps/api/app/routers/report.py`
- `/apps/api/app/routers/articles.py`
- `/apps/api/app/main.py`
- `/apps/mobile/app/(tabs)/index.tsx`
- `/apps/mobile/lib/report.ts`
- `/apps/mobile/lib/date.ts`
- `/apps/mobile/app/article/[articleId].tsx`

## What is currently stable

- 리포트 목록/필터/상세 흐름이 모바일에서 동작 가능한 형태로 연결됐다(데이터는 API 기반).

## What remains

- Step 12 완료 처리(상태 반영): `python tools/devlog.py complete 12`

## Exact next implementation boundary

- **Boundary**: Step 13에서는 “알림(예약/권한/딥링크)”만 구현한다.
  - 알림 시간 설정 값(NotificationSetting) 저장/조회
  - 모바일에서 권한 요청 및 로컬 알림 예약
  - 알림 클릭 시 해당 날짜 리포트로 딥링크 진입
- **Completion criteria**:
  - 권한 허용/거부 시나리오 포함, 알림 트리거 및 딥링크 진입이 확인된다

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-12.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.

