# Supabase MCP 참조 (touch 프로젝트)

Supabase MCP로 이 프로젝트를 정리·확인할 때 쓰는 체크리스트와 환경 변수 요약.

---

## 0. 이 프로젝트의 Supabase MCP 설정

- **서버 URL**: `https://mcp.supabase.com/mcp?project_ref=jodarpqalwttovzsdnts`
- **Project ref**: `jodarpqalwttovzsdnts` (이 프로젝트 전용 Supabase 프로젝트로 스코프됨)
- **설정 위치**: `.cursor/mcp.json` (프로젝트 루트)

Cursor에서 한 번만 하면 됨:

1. **Settings → Cursor Settings → Tools & MCP** 에서 Supabase가 목록에 있는지 확인.
2. 없으면 Cursor 재시작 후, MCP 추가 시 브라우저에서 Supabase 로그인·조직 권한 허용.
3. 연결 후 "What tables are there? Use MCP tools." 등으로 동작 확인.

`project_ref` 가 있으면 해당 프로젝트만 접근 가능하고, 계정 관리 도구(`list_projects`, `create_project` 등)는 비활성화됨.

---

## 1. MCP로 할 수 있는 작업 매핑

| 목적 | MCP 도구 | 비고 |
|------|----------|------|
| 프로젝트 목록/상세 | `list_projects`, `get_project` | 연결된 Supabase 프로젝트 확인 |
| DB 연결 정보 | `get_project` → Settings → Database URI | `DATABASE_URL`에 넣을 값 |
| API URL / 퍼블릭 키 | `get_project_url`, `get_publishable_keys` | 프론트 `EXPO_PUBLIC_*` 또는 REST 연동 시 참고 |
| 테이블 목록 확인 | `list_tables` | 스키마 생성 여부 검증 |
| SQL 직접 실행 | `execute_sql` | 수동 스키마 또는 데이터 보정 |
| 마이그레이션 적용 | `apply_migration` | DDL 파일이 있을 때 |
| 로그/디버깅 | `get_logs` | API·Postgres·Auth 등 |
| TypeScript 타입 생성 | `generate_typescript_types` | 프론트 타입 동기화 시 |

프로젝트 생성은 대시보드에서 하는 것을 권장. MCP로 생성하려면 `create_project` 사용 (비용 확인 `get_cost` / `confirm_cost` 필요할 수 있음).

---

## 2. Vercel에 넣을 환경 변수 키 (복사용)

### API (apps/api) — Vercel Environment Variables

```
DATABASE_URL
JWT_SECRET
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRES_MINUTES
STOCK_PRICE_API_KEY
DART_API_KEY
OPENAI_API_KEY
PROCESSOR_MODE
COLLECTOR_MODE
```

- **필수**: `DATABASE_URL`, `JWT_SECRET`
- `DATABASE_URL`: Supabase **Settings → Database** 의 Connection string (URI, `?sslmode=require` 포함). MCP `get_project`로 프로젝트 확인 후 대시보드에서 복사.

### 프론트 (apps/mobile) — Vercel Environment Variables

```
EXPO_PUBLIC_API_BASE_URL
```

- 값 예: `https://api-xxxx.vercel.app` (API 배포 URL)

---

## 3. 배포 순서 요약

1. **Supabase**: 프로젝트 있음 확인 (`list_projects` / `get_project`) → 없으면 대시보드에서 생성.
2. **DATABASE_URL**: Supabase Database URI 복사 → Vercel API 프로젝트 env에 `DATABASE_URL` 설정.
3. **Vercel API**: `apps/api`에서 `npx vercel --prod --yes` → 배포 URL 확보.
4. **Vercel 프론트**: `EXPO_PUBLIC_API_BASE_URL`에 위 API URL 설정 → `apps/mobile`에서 `npx vercel --prod --yes`.
5. **검증**: API `/health` 호출 → 필요 시 `list_tables`로 Supabase에 테이블 생성 여부 확인.

---

## 4. 이 프로젝트의 테이블 (SQLModel)

스키마는 앱의 `init_db()`로 생성되며, 아래 테이블명은 `apps/api/app/models.py` 기준 참고용.

- user, keyword, article, articlekeyword, processingresult, notificationsetting  
- memberprofile, memberaccesslog, memberactionlog, adminuser, servicemodule, adminauditlog  
- appsetting, pointadjustmentrequest, watchitem, signalruleconfig, stockapiusagelog  
- pushtoken, signaleventlog, corpcodecache  

MCP `list_tables`로 위 테이블 존재 여부 확인 가능.
