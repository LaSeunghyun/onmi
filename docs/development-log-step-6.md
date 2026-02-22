# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 6
- **Goal**: 모듈형 모바일 앱 + 1차 모듈(키워드 뉴스 리포트)의 **결정사항(정책/데이터/상태/IA/파이프라인)** 을 단일 소스로 고정하고, 제품 개발 단계 계획을 확정한다.

## Completed implementations (this step)

- PRD 결정사항 고정(요약):
  - **플랫폼**: 모바일 only(iOS/Android)
  - **로그인**: 필수(계정별 키워드/설정 분리)
  - **키워드**: 무제한 + **활성/비활성 토글**(배치 대상 제어) + (권장) 핀
  - **기간 기준**: KST 00:00~23:59
  - **수집 정책**: **검색 API 우선**, 무료 쿼터 소진/오류 시 **RSS 폴백**
  - **처리 순서**: **원문 기준 요약/분류 → 한국어 번역(표시용)**
  - **콘텐츠 제공**: 요약 + 원문 링크(원문 미러링 저장 없음)
  - **감성 라벨**: 긍정/중립/부정(강조 없이 중립 위계)
- 화면/상태(필수):
  - 리포트: 로딩/빈/에러/partial/폴백(RSS)/번역 실패 상태
  - 키워드: 무제한 대응(검색/섹션/토글) + 활성 0개 상태
- IA 권장안:
  - 하단 탭 2개: **리포트 / 키워드**
  - 설정은 헤더(톱니)에서 진입
- 제품 개발 Ordered Steps 확정(DEVLOG Step 7~14로 연결)

## Files modified

- `/devlog/DEVELOPMENT_LOG.md`
- `/docs/development-log-step-6.md`

## What is currently stable

- 제품 개발에 필요한 정책/데이터/상태/IA/파이프라인의 결정본이 고정되었고, 다음 Step부터는 이 문서의 경계만 따라 구현하면 된다.

## What remains

- Step 6 완료 처리(상태 반영): `python tools/devlog.py complete 6`

## Exact next implementation boundary

- **Boundary**: Step 7에서는 **스캐폴딩만** 수행한다.
  - `apps/mobile` Expo 앱 생성 + 기본 라우팅(빈 화면)
  - `apps/api` FastAPI 서버 생성 + SQLite 연결 + `/health` 엔드포인트
  - 실행 방법/환경변수/README 정리
- **Completion criteria**:
  - 모바일 앱이 로컬에서 부팅되어 기본 화면이 표시된다.
  - API 서버가 로컬에서 부팅되고 `/health`가 200을 반환한다.

## Resume instructions (context reset)

1) 워크스페이스 루트(`touch/`)에서 실행:

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

2) 이 로그(`/docs/development-log-step-6.md`)와 `devlog/CONTEXT.md`를 읽고, “Exact next implementation boundary”만 수행한다.

