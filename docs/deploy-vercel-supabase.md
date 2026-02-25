# Vercel + Supabase 배포 가이드

**Supabase MCP 사용 시**: [supabase-mcp-reference.md](./supabase-mcp-reference.md)에 MCP 도구 매핑·환경 변수 키·배포 순서 요약이 정리되어 있음.

---

## 1. Supabase 설정 (DB)

### 1.1 프로젝트 생성

1. [Supabase 대시보드](https://supabase.com/dashboard) 로그인
2. **New project** → Organization 선택, 프로젝트 이름·비밀번호·리전 설정 후 생성
3. 프로젝트가 준비될 때까지 대기 (약 2분)

### 1.2 연결 정보 복사

1. 프로젝트 → **Settings** → **Database**
2. **Connection string** → **URI** 탭 선택
3. **Mode**: **Session** (또는 Serverless용이면 **Transaction** 풀러 사용 시 포트 6543)
4. 비밀번호를 실제 값으로 치환한 URL 복사  
   형식:  
   `postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require`  
   또는 직접 연결:  
   `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require`

### 1.3 스키마 생성

이 API는 **SQLModel**로 테이블을 정의하며, 앱 기동 시 `init_db()`에서 `SQLModel.metadata.create_all(engine)`으로 테이블을 생성합니다.  
즉, **별도 SQL 마이그레이션 없이** 첫 요청(또는 Cold start) 시 Supabase Postgres에 테이블이 생성됩니다.

- 최초 배포 후 `/health` 호출만으로는 테이블이 생성되지 않을 수 있음  
- DB를 쓰는 엔드포인트를 한 번 호출하면 테이블이 생성됨  
- 수동으로 스키마를 넣고 싶다면 Supabase **SQL Editor**에서 모델에 맞는 DDL 실행 가능

### 1.4 로컬 SQLite → Supabase 이전

로컬에 쌓아 둔 SQLite 데이터를 Supabase로 한 번에 옮기려면 **마이그레이션 스크립트**를 사용한다.

1. `apps/api`에서 가상환경 활성화 후 실행:
   ```powershell
   cd apps\api
   .\.venv\Scripts\Activate.ps1
   $env:TARGET_DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.jodarpqalwttovzsdnts.supabase.co:5432/postgres?sslmode=require"
   python -m scripts.migrate_sqlite_to_supabase
   ```
2. **SOURCE_DATABASE_URL**: 로컬 DB (기본값 `sqlite:///./data/touch.db`, `apps/api` 기준).
3. **TARGET_DATABASE_URL**: Supabase Postgres URI (필수, 비밀번호 치환, `?sslmode=require` 포함).
4. 스크립트가 Supabase에 스키마를 만든 뒤, FK 순서대로 테이블별로 데이터를 복사한다.  
   Supabase 쪽이 비어 있을 때만 사용할 것. 이미 데이터가 있으면 PK 중복 오류가 난다.

---

## 2. Vercel 배포 (API)

### 2.1 로그인 (최초 1회)

```powershell
cd c:\Users\wisebirds\Documents\touch\apps\api
npx vercel login
```

브라우저에서 로그인 완료 후 터미널로 돌아옵니다.

### 2.2 환경 변수 설정

Vercel 대시보드에서 할 경우:

1. [Vercel Dashboard](https://vercel.com/dashboard) → 프로젝트 선택 (또는 첫 배포 후 생성된 프로젝트)
2. **Settings** → **Environment Variables**
3. 아래 변수 추가 (Production, Preview, Development 원하는 것에 체크)

| Name | Value | 비고 |
|------|--------|------|
| `DATABASE_URL` | Supabase에서 복사한 Postgres URL | `?sslmode=require` 포함, 비밀번호 치환 |
| `JWT_SECRET` | 임의의 긴 비밀 문자열 | 토큰 서명용 |
| `STOCK_PRICE_API_KEY` | (선택) 공공데이터 API 키 | 감시종목 기능 사용 시 |
| `DART_API_KEY` | (선택) DART API 키 | 감시종목 기능 사용 시 |

CLI로 할 경우 (배포 전):

```powershell
cd c:\Users\wisebirds\Documents\touch\apps\api
npx vercel env add DATABASE_URL
npx vercel env add JWT_SECRET
# 프롬프트에 따라 값 입력
```

### 2.3 배포 실행

```powershell
cd c:\Users\wisebirds\Documents\touch\apps\api
npx vercel --prod
```

- 최초 실행 시 프로젝트 연결 여부를 묻으면 **Y** 후 진행
- Root Directory는 **현재 디렉터리(`apps/api`)** 로 자동 인식됨 (`vercel.json` 기준)

### 2.4 배포 확인

- 터미널에 출력되는 URL (예: `https://touch-api-xxx.vercel.app`) 에서:
  - `GET https://<배포URL>/health` → `{"status":"ok"}` 확인
  - DB 사용 엔드포인트 1회 호출 후 Supabase **Table Editor**에서 테이블 생성 여부 확인

---

## 3. Vercel 배포 (프론트엔드 · Expo 웹)

프론트는 **Expo** 앱의 웹 빌드를 정적 사이트로 내보낸 뒤 Vercel에 올립니다.

### 3.1 준비

- `apps/mobile`에 `vercel.json`이 있으면 **Build Command** / **Output Directory** / SPA 라우팅이 이미 설정되어 있음
- 로컬에서 웹 빌드 확인: `cd apps/mobile` → `npm run build:web` → `dist/` 생성 확인

### 3.2 배포

```powershell
cd c:\Users\wisebirds\Documents\touch\apps\mobile
npx vercel --prod --yes
```

- 최초 실행 시 Vercel이 새 프로젝트를 만들 수 있음 (API와는 **별도 프로젝트**로 두는 것을 권장)
- Root Directory는 `apps/mobile`로 두고, 빌드 명령·출력 디렉터리는 `vercel.json` 값 사용

### 3.3 환경 변수 (필요 시)

- API URL 등 프론트 전용 변수가 있으면 Vercel 프로젝트 **Settings → Environment Variables**에 추가
- 빌드 시 주입하려면 변수 이름에 `NEXT_PUBLIC_` 또는 `EXPO_PUBLIC_` 접두사 사용 후 코드에서 참조

### 3.4 확인

- 배포 URL 접속 후 로그인·탐색 등 동작 확인
- 새로고침·직접 URL 접근 시에도 SPA 라우팅이 동작하는지 확인 (`vercel.json`의 `rewrites`로 `index.html` 폴백 처리됨)

---

## 4. 요약 체크리스트

- [ ] Supabase 프로젝트 생성 (또는 MCP `list_projects` / `get_project`로 확인)
- [ ] `DATABASE_URL` 복사 (비밀번호 치환, `?sslmode=require` 포함)
- [ ] `vercel login` 실행
- [ ] Vercel **API** 프로젝트: `DATABASE_URL`, `JWT_SECRET` 등 설정
- [ ] Vercel **프론트** 프로젝트: `EXPO_PUBLIC_API_BASE_URL` = API 배포 URL
- [ ] `apps/api`에서 `npx vercel --prod --yes` 실행
- [ ] `apps/mobile`에서 `npx vercel --prod --yes` 실행 (프론트)
- [ ] 배포 URL `/health` 및 DB 연동 엔드포인트 확인 (필요 시 MCP `list_tables`로 스키마 검증)

---

## 5. 트러블슈팅

| 현상 | 확인 사항 |
|------|-----------|
| 배포 시 "token not valid" | `npx vercel login` 다시 실행 |
| DB 연결 오류 | `DATABASE_URL`에 `?sslmode=require` 있는지, 비밀번호 특수문자 URL 인코딩 여부 확인 |
| Cold start 후 타임아웃 | Vercel 무료 플랜 제한; Supabase Connection pooler(Transaction 모드, 포트 6543) 사용 권장 |
| 테이블 없음 | DB를 쓰는 API 한 번 호출 후 Supabase Table Editor에서 확인 |
