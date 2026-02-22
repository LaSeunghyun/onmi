# Project: touch (모듈형 모바일 앱)

## Current step

- **Step number**: 8
- **Goal**: 로그인 필수 인증(API + 모바일 연동)을 구현한다.

## Completed implementations (this step)

### API (FastAPI)

- 인증 엔드포인트 추가
  - `POST /auth/signup` (이메일 + 비밀번호)
  - `POST /auth/login`
  - `GET /me` (Bearer 토큰 필요)
- 비밀번호 해시: Windows 호환성을 위해 **PBKDF2** 기반(passlib) 사용
- JWT 액세스 토큰 발급 및 검증(`sub = user_id`)
- 로컬 SQLite DB 초기화(create_all) 및 CORS 허용(개발 편의)
- `.env.example` 추가

### Mobile (Expo)

- 토큰 저장: `expo-secure-store`
- 인증 컨텍스트(`AuthProvider`) 및 부팅 시 토큰 복원 + `/me` 검증
- 라우트 가드: 비로그인 상태에서는 `/(auth)/login`으로 리다이렉트
- 로그인/회원가입 화면 추가

## Files modified

- `/apps/api/app/main.py`
- `/apps/api/app/settings.py`
- `/apps/api/app/db.py`
- `/apps/api/app/models.py`
- `/apps/api/app/security.py`
- `/apps/api/app/routers/auth.py`
- `/apps/api/app/routers/me.py`
- `/apps/api/requirements.txt`
- `/apps/api/.env.example`
- `/apps/mobile/app/_layout.tsx`
- `/apps/mobile/app/(auth)/*`
- `/apps/mobile/lib/*`

## What is currently stable

- API에서 회원가입/로그인 후 토큰으로 `/me` 호출이 성공한다(스모크 테스트 확인).
- 모바일은 토큰 기반으로 로그인 전 접근이 차단되고, 로그인 성공 시 세션이 저장된다.

## What remains

- Step 8 완료 처리(상태 반영): `python tools/devlog.py complete 8`

## Exact next implementation boundary

- **Boundary**: Step 9에서는 “키워드 무제한 관리(검색/핀/활성 토글)”만 구현한다.
  - API: 키워드 CRUD + 상태 필드(is_active/is_pinned) + 목록 검색/정렬 파라미터
  - Mobile: 키워드 탭 UI(검색, 핀/활성/비활성 섹션, 토글, 삭제, 추가)
  - 리포트/수집/번역/분류는 구현하지 않는다
- **Completion criteria**:
  - 100개 키워드에서도 검색/토글/핀/삭제가 매끄럽고 DB에 영속 저장된다
  - 활성/비활성 상태가 다음 단계(리포트 배치 대상)로 전달 가능하도록 API/DB 모델이 확정된다

## Resume instructions (context reset)

```powershell
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py status
```

그 다음 `/docs/development-log-step-8.md`와 `devlog/CONTEXT.md`를 읽고 “Exact next implementation boundary”만 수행한다.

