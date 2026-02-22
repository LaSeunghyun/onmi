## touch (모듈형 모바일 앱)

### 구성

- `apps/mobile`: 모바일 앱(Expo)
- `apps/api`: API 서버(FastAPI)

### 빠른 실행

#### API

```powershell
cd apps/api
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
```

#### Mobile

```powershell
cd apps/mobile
npm install
npx expo start
```

