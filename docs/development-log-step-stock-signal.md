# Development Log: 주식 신호·알림 기능 (Step 완료)

## 프로젝트
touch

## 완료 범위
- 최종 PRD 및 리플래시 정책 확정 문서
- Design System 확장 (토큰·컴포넌트 기준)
- API: 감시종목·신호규칙·시그널 대시보드·시세/공시/신호 엔진·쿼터 로그
- Mobile: 감시종목 탭·종목 추가·종목 상세·디자인 토큰 적용
- QA 체크리스트 작성 및 API/TS 검증 완료

## 수정/추가된 파일

### 문서
- `docs/PRD-stock-signal-notification.md` — 최종 확정안·리플래시 정책
- `docs/design-system-stock-feature.md` — 디자인 시스템 확장
- `docs/QA-stock-signal-notification.md` — QA 체크리스트
- `docs/development-log-step-stock-signal.md` — 본 로그

### API (apps/api)
- `app/models.py` — WatchItem, SignalRuleConfig, StockApiUsageLog, PushToken, SignalEventLog
- `app/settings.py` — stock_price_api_key, dart_api_key
- `app/services/__init__.py`
- `app/services/stock_price.py` — 공공데이터 getStockPriceInfo
- `app/services/dart.py` — DART list API
- `app/services/signal_engine.py` — MACD/EMA/거래량/퍼센트 규칙
- `app/services/disclosure_sentiment.py` — 공시 감성 분류
- `app/services/quota.py` — 일일 한도·권장 주기
- `app/routers/stocks.py` — watchlist, rules, signals
- `app/main.py` — stocks router 등록

### Mobile (apps/mobile)
- `theme/tokens.ts` — signal.*, disclosure.*
- `lib/stocks.ts` — API 클라이언트
- `app/(tabs)/_layout.tsx` — 감시종목 탭·헤더 추가 버튼
- `app/(tabs)/stocks.tsx` — 감시종목 목록·신호/공시 배지·당겨서 새로고침
- `app/stock/_layout.tsx` — 스택 레이아웃
- `app/stock/add.tsx` — 종목 추가 폼
- `app/stock/[corpCode].tsx` — 종목 상세·근거·공시 요약

## 현재 안정 상태
- 인증 후 감시종목 CRUD·순서/즐겨찾기·신호 규칙·시그널 대시보드 API 동작
- 앱: 감시종목 탭에서 목록·추가·상세·신호/공시 표시
- 시세/공시 API 키 미설정 시에도 목록·규칙·빈 신호 응답 정상

## 미구현 (다음 단계 후보)
- 푸시 발송 (SignalEventLog·PushToken 연동, 조건 충족 시 Expo Push)
- 리플래시 주기 앱 설정 (60/120/300초)
- 한도 70%/85% 도달 시 주기 자동 확대 (백엔드 스케줄러 또는 앱 폴링)

## 다음 구현 경계
- Step: 푸시 알림 파이프라인 (토큰 등록·신호 전환 시 발송·쿨다운)

## 재개 방법
1. `docs/PRD-stock-signal-notification.md`·`docs/QA-stock-signal-notification.md` 확인
2. API: `STOCK_PRICE_API_KEY`, `DART_API_KEY` 환경변수 설정 후 `/stocks/signals` 호출로 시세·공시 반영 확인
3. 모바일: 로그인 → 감시종목 탭 → 종목 추가 → 신호/공시 확인
