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

1. Vercel 프로젝트 생성 후 **Root Directory**를 `apps/api`로 지정
2. Environment Variables 설정
   - `DATABASE_URL` (Supabase Postgres URL, `?sslmode=require` 포함)
   - `JWT_SECRET`
   - `OPENAI_API_KEY` (필요 시)
3. Deploy 실행
4. 배포 URL에서 `GET /health` 확인

`vercel.json`은 모든 요청을 FastAPI 엔트리(`api/index.py`)로 리라이트한다.

