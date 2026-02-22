# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 10
- **Goal**: 뉴스 수집 파이프라인(검색 API 우선 + RSS 폴백)과 저장(중복 제거)을 구현한다.

## Completed implementations (this step)

### API

- 수집 파이프라인 의존성 추가
  - `httpx`, `feedparser`, `python-dateutil`, `tzdata`(Windows 타임존)
- 데이터 모델 추가
  - `Article`(user/date_kst/canonical_url 기반)
  - `ArticleKeyword`(기사-키워드 연결)
  - 중복 제거: `(user_id, canonical_url)` 유니크
- 수집기 구현 (`app/collect.py`)
  - **검색 API 우선**: GDELT Doc API
  - **RSS 폴백**: Google News RSS(ko-KR + en-US)
  - KST 00:00~23:59 기준으로 날짜 범위 계산(UTC 변환)
  - URL 캐노니컬라이즈(utm_* 제거)
  - Windows tzdata 누락 대비 폴백(고정 +09:00)
  - 네트워크 지연 대비 타임아웃 상향(30s)
  - 개발/차단 환경 대비 `COLLECTOR_MODE=mock` 지원
- 온디맨드 실행 엔드포인트 추가
  - `POST /collect?date_kst=YYYY-MM-DD` (기본: 오늘 KST)
  - 활성 키워드만 대상으로 수집/저장
  - 응답에 `search_items`, `rss_items`, `inserted_articles` 포함

### 검증

- `COLLECTOR_MODE=mock`에서:
  - 검색 경로 삽입(inserted_articles >= 1) 확인
  - `force_rss` 키워드로 RSS 폴백 경로(rss_items >= 1) 확인

## Files modified

- `/apps/api/requirements.txt`
- `/apps/api/app/settings.py`
- `/apps/api/app/models.py`
- `/apps/api/app/collect.py`
- `/apps/api/app/routers/collect.py`
- `/apps/api/app/main.py`

## What is currently stable

- “활성 키워드만 대상으로 검색 우선 → 실패/빈 결과 시 RSS 폴백 → 중복 제거 후 저장” 파이프라인이 동작한다.

## What remains

- Step 10 완료 처리(상태 반영): `python tools/devlog.py complete 10`

## Exact next implementation boundary

- **Boundary**: Step 11에서는 “원문 요약/감성 분류 + 결과 번역”만 구현한다.
  - 저장된 Article에 대해 ProcessingResult를 생성/저장
  - 원문 기준 요약/분류 후 한국어 번역(표시용)
  - 번역 실패 시 상태 기록 + 원문 링크 중심 처리
  - UI(리포트 화면)는 Step 12에서 구현
- **Completion criteria**:
  - (mock 또는 live) 영문 기사 1건에서 `summary_ko`와 `sentiment`가 생성된다
  - 번역 실패 상태가 API 응답/DB에 남는다

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-10.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.

