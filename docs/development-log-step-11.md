# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 11
- **Goal**: 원문 기준 요약/감성 분류 후 한국어 번역 결과를 생성(저장)한다.

## Completed implementations (this step)

### API

- `ProcessingResult` 테이블/모델 추가
  - `sentiment`, `sentiment_confidence`
  - `summary_original`, `summary_ko`
  - `translation_status`, `translated_from`
  - `(article_id)` 유니크(1:1)
- 처리 로직 추가
  - `app/process.py`: `PROCESSOR_MODE=mock` 기본
    - 원문(타이틀/스니펫) 기반 요약 생성
    - 감성 분류(기본 neutral)
    - 원문이 한국어가 아니면 `summary_ko`에 번역 표시 + `translation_status=completed`
- 엔드포인트 추가
  - `POST /process?date_kst=YYYY-MM-DD` (기본: 오늘 KST)
  - 해당 날짜 Article 중 처리되지 않은 것만 ProcessingResult 생성(멱등)

### 검증

- `COLLECTOR_MODE=mock`, `PROCESSOR_MODE=mock`에서:
  - `POST /collect`로 Article 삽입
  - `POST /process`로 ProcessingResult 생성(`processed_new >= 1`) 확인

## Files modified

- `/apps/api/app/settings.py`
- `/apps/api/app/models.py`
- `/apps/api/app/process.py`
- `/apps/api/app/routers/process.py`
- `/apps/api/app/main.py`

## What is currently stable

- 저장된 Article에 대해 “요약/감성/번역 상태” 결과가 생성·저장되는 파이프라인이 준비됐다.

## What remains

- Step 11 완료 처리(상태 반영): `python tools/devlog.py complete 11`

## Exact next implementation boundary

- **Boundary**: Step 12에서는 “리포트 UX 완성(날짜/필터/상태)”만 구현한다.
  - API: 리포트 조회용 엔드포인트(기사 + 처리결과 + 키워드 필터)
  - Mobile: 리포트 화면(요약 카드/필터/날짜 선택/리스트/상태)
  - 알림은 Step 13에서 구현
- **Completion criteria**:
  - 모바일에서 날짜 변경/키워드 필터가 동작하고, 로딩/빈/에러 상태가 표현된다
  - 번역 실패/폴백 상태(데이터 존재 시)가 UI에 표시된다

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-11.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.

