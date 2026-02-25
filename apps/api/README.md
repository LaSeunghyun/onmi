## touch API (FastAPI)

### 로컬 실행 (Windows PowerShell)

```powershell
cd apps/api

# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 의존성 설치(최초 1회)
python -m pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --port 8010
```

### 헬스체크

- `GET http://localhost:8010/health` → `{"status":"ok"}`

### Vercel + Supabase 배포

상세 단계는 **[/docs/deploy-vercel-supabase.md](../../docs/deploy-vercel-supabase.md)** 참고.

**요약**

1. Supabase에서 프로젝트 생성 후 `DATABASE_URL` 복사 (Postgres URI, `?sslmode=require` 포함)
2. `npx vercel login` (최초 1회)
3. Vercel 프로젝트에서 Environment Variables 설정: `DATABASE_URL`, `JWT_SECRET` 등
4. 배포: `apps/api`에서 `npx vercel --prod` 또는 `.\deploy.ps1`

Vercel 프로젝트 **Root Directory**는 `apps/api`로 두면 됨. `vercel.json`이 모든 요청을 FastAPI 엔트리(`api/index.py`)로 리라이트한다.

