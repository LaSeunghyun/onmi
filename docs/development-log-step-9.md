# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 9
- **Goal**: 키워드 무제한 관리(검색/핀/활성 토글/삭제/추가)를 API+모바일에 구현한다.

## Completed implementations (this step)

### API

- `Keyword` 테이블/모델 추가
  - `text`, `is_active`, `is_pinned`, `last_used_at`, `created_at`, `updated_at`
- 인증 필요 키워드 API 추가
  - `GET /keywords` (q, status_filter, sort)
  - `POST /keywords`
  - `PATCH /keywords/{keyword_id}` (핀/활성 토글)
  - `DELETE /keywords/{keyword_id}`
- 공통 인증 의존성(`get_current_user`)를 `app/deps.py`로 분리해 재사용
- 간단 스트레스 테스트: 120개 키워드 생성 후 목록/검색 동작 확인

### Mobile

- 탭 구성 개선(표기/아이콘): `리포트`, `키워드`
- 키워드 탭 UI 구현
  - 검색(디바운스)
  - 추가 입력 + 플러스 버튼
  - 섹션(핀/활성/비활성)
  - 핀 토글(별 아이콘), 활성 토글(Switch), 삭제(휴지통 + 확인)
- 설정 모달 최소 구성: 로그인 이메일/API URL 표시 + 로그아웃

## Files modified

- `/apps/api/app/models.py`
- `/apps/api/app/deps.py`
- `/apps/api/app/routers/keywords.py`
- `/apps/api/app/routers/me.py`
- `/apps/api/app/main.py`
- `/apps/mobile/app/(tabs)/two.tsx`
- `/apps/mobile/app/(tabs)/_layout.tsx`
- `/apps/mobile/lib/keywords.ts`
- `/apps/mobile/app/modal.tsx`

## What is currently stable

- 키워드가 많아져도(테스트: 120개) 목록/검색이 API에서 정상 동작한다.
- 모바일에서 키워드 추가/검색/핀/활성 토글/삭제 플로우가 완성돼 있다.

## What remains

- Step 9 완료 처리(상태 반영): `python tools/devlog.py complete 9`

## Exact next implementation boundary

- **Boundary**: Step 10에서는 “뉴스 수집 파이프라인(검색 API 우선 + RSS 폴백)”만 구현한다.
  - 검색 API 우선 수집(키워드별)
  - 무료 쿼터 소진/오류 시 RSS 폴백(키워드별)
  - 중복 제거(canonical_url 기준)
  - 저장: Article 엔티티(원문 메타 + snippet)
  - UI는 리포트 생성/표시가 아니라 **수집 파이프라인까지**로 제한
- **Completion criteria**:
  - 활성 키워드만 대상으로 KST 당일 기사 수집이 수행된다
  - 검색 API 실패 시 RSS 폴백이 동작하고 폴백 여부가 기록된다

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-9.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.

