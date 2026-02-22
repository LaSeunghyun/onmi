# QA: 주식 신호·알림 기능

## 완료일
2025-02-22

## 체크리스트

### 핵심 플로우
- [x] 감시종목 목록 조회 (GET /stocks/watchlist, 인증 필요)
- [x] 감시종목 추가 (POST /stocks/watchlist, corp_code 8자리 + srtn_cd 6자리, 최대 10개)
- [x] 감시종목 삭제 (DELETE /stocks/watchlist/:id)
- [x] 즐겨찾기 토글 (PATCH /stocks/watchlist/:id/favorite)
- [x] 순서 변경 (PATCH /stocks/watchlist/reorder, ordered_ids)
- [x] 신호 규칙 조회/수정 (GET/PUT /stocks/rules)
- [x] 신호 대시보드 (GET /stocks/signals → 종목별 signal, reasons, disclosure_sentiment, disclosure_summary)
- [x] 앱: 감시종목 탭 목록·당겨서 새로고침·종목 상세(근거·공시 요약)·종목 추가 화면

### 권한/보안
- [x] /stocks/* 인증 필수 (401 미인증)
- [x] API 키는 settings (env) 기반, 코드에 노출 없음

### 엣지 케이스
- [x] 10개 초과 등록 시 400
- [x] 동일 corp_code 중복 등록 시 409
- [x] 시세/공시 API 미설정 시 signals는 데이터 없음·hold·근거 "데이터 없음"
- [x] 쿼터 로그(StockApiUsageLog) 일별 누적

### 성능/구현
- [x] 10종목 기준 signals 1회 호출 시 시세 10회 + 공시 N회, 쿼터 카운트 반영
- [x] 디자인 토큰: signal.buy/sell/hold, disclosure.positive/neutral/negative, 기존 space/radius/font

## 테스트 실행

```bash
# API
cd apps/api && .venv\Scripts\Activate.ps1
python -c "
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app)
assert c.get('/stocks/watchlist').status_code == 401
assert c.get('/health').status_code == 200
print('API QA passed')
"

# Mobile (수동)
# 1. npm start in apps/mobile
# 2. 로그인 후 감시종목 탭 이동
# 3. + 버튼으로 종목 추가 (corp_code 8자리, srtn_cd 6자리)
# 4. 목록에서 즐겨찾기·상세 진입·당겨서 새로고침 확인
```

## 미구현 (추가 단계)
- 푸시 발송: 조건 충족 시 Expo Push 전송 (SignalEventLog + PushToken 연동)
- 리플래시 주기 앱 설정: 60/120/300초 선택 UI
- 한도 70%/85% 도달 시 주기 자동 확대 (백엔드 스케줄러 또는 앱 폴링 시 적용)
