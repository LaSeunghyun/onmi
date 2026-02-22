# Project: touch (API 배포 전환: Vercel + Supabase)

## Current step

- **Step number**: 19
- **Goal**: FastAPI API를 Vercel 서버리스 환경에 맞추고 DB를 Supabase Postgres로 전환 가능한 상태로 만든다.

## Completed implementations (this step)

### Deployment entry and routing

- Vercel 엔트리 파일 추가
  - `apps/api/api/index.py`
- Vercel 리라이트 설정 추가
  - `apps/api/vercel.json`
  - 모든 요청을 FastAPI 엔트리로 전달

### Database portability (SQLite -> Postgres ready)

- DB URL 정규화 로직 추가 (`postgres://`, `postgresql://` -> `postgresql+psycopg://`)
  - `apps/api/app/db.py`
- 런타임별 엔진 옵션 분리
  - SQLite: `check_same_thread=False`
  - Postgres: `pool_pre_ping=True`, `pool_size=1`, `max_overflow=0`
- SQLite 디렉터리 자동 생성 로직은 로컬 개발용으로 유지

### Dependencies and env template

- Postgres 드라이버 추가
  - `apps/api/requirements.txt` (`psycopg[binary]`)
- 환경변수 예시를 Supabase 중심으로 갱신
  - `apps/api/.env.example`

### Documentation

- 배포 가이드(Vercel Root Directory/환경변수/헬스체크) 추가
  - `apps/api/README.md`

### Validation

- `apps/api`: `python -m compileall app` 통과
- 편집 파일 lint diagnostics 오류 없음

## Files modified

- `/apps/api/app/db.py`
- `/apps/api/requirements.txt`
- `/apps/api/.env.example`
- `/apps/api/api/index.py` (new)
- `/apps/api/vercel.json` (new)
- `/apps/api/README.md`

## What is currently stable

- Vercel에서 FastAPI 단일 엔트리로 라우팅되는 배포 구조가 준비되었다.
- `DATABASE_URL`만 Supabase 값으로 넣으면 Postgres 연결이 가능하다.

## What remains

- Vercel 프로젝트 생성 후 Root Directory를 `apps/api`로 지정
- Vercel 환경변수(`DATABASE_URL`, `JWT_SECRET`) 주입
- Supabase에 스키마 생성(초기 기동/마이그레이션)
- 배포 URL `/health` 검증

## Exact next implementation boundary

- **Boundary**: 운영 배포 검증 및 스키마 마이그레이션 체계화
- **Completion criteria**:
  - Vercel 프로덕션 배포 1회 성공
  - Supabase 스키마 생성 재현 가능한 절차 문서화
  - 실패 시 롤백/재배포 체크리스트 작성

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-19.md`를 읽고 “Exact next implementation boundary”만 수행한다.

