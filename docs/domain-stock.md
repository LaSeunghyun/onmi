# Stock 도메인

주식 감시종목 관리와 규칙 기반 매수·매도 신호 생성을 담당하는 도메인.

---

## 역할

- 감시종목(Watchlist) CRUD 및 정렬·즐겨찾기
- 사용자별 신호 규칙 설정 (손절/익절/EMA 기울기/거래량)
- 주식 시세 조회 및 기술적 분석 신호 계산
- DART 공시 감성 분석
- 시세 API 일일 쿼터 관리
- Expo 푸시 알림 토큰 관리
- 신호 이벤트 전량 로그 기록

---

## 모델

### `WatchItem`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User) | |
| `corp_code` | str(8) | DART 고유번호 8자리 (앞에 `0` 패딩) |
| `srtn_cd` | str(6) | 종목코드 6자리 (시세 API용) |
| `itms_nm` | str? | 종목명 |
| `sort_order` | int | 정렬 순서 (수동 드래그 지원) |
| `is_favorite` | bool | 즐겨찾기 여부 |
| `created_at` | datetime | |
| `updated_at` | datetime | |

> user_id + corp_code 유니크. 사용자당 최대 `settings.max_watch_items`개 (기본 10개).
> 정렬: 즐겨찾기 우선 → sort_order 오름차순 → updated_at 내림차순

### `SignalRuleConfig`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User, unique) | 1:1 관계 |
| `stop_loss_pct` | float? | 손절 기준 % (예: `-3.0`) |
| `take_profit_pct` | float? | 익절 기준 % (예: `7.0`) |
| `ema_slope_threshold` | float | 25일 EMA 기울기 최소값. 기본 `0.0` |
| `volume_ratio_on` | bool | 거래량 조건 사용 여부. 기본 `true` |
| `volume_ratio_multiplier` | float | 20일 평균 대비 배수. 기본 `1.5` |
| `push_enabled` | bool | 푸시 알림 ON/OFF. 기본 `true` |
| `updated_at` | datetime | |

### `StockApiUsageLog`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `date_kst` | str(10) | `YYYY-MM-DD` (KST 기준) |
| `call_count` | int | 당일 누적 API 호출 수 |
| `updated_at` | datetime | |

> 금융위원회 시세 API 일일 한도: **10,000회 / 30 TPS**

### `PushToken`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User, unique) | 1:1 관계 |
| `token` | str | Expo 푸시 토큰 |
| `updated_at` | datetime | |

### `SignalEventLog`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User) | |
| `corp_code` | str(8) | DART 고유번호 |
| `signal_type` | str | `buy` \| `sell` \| `hold` |
| `reason_codes` | str? | 판정 근거 목록 (JSON 문자열) |
| `push_sent` | bool | 푸시 발송 여부 |
| `created_at` | datetime | |

### `CorpCodeCache`
| 필드 | 타입 | 설명 |
|------|------|------|
| `corp_code` | str(8) (PK) | DART 고유번호 |
| `corp_name` | str(200, index) | 회사명 |
| `stock_code` | str(6, index) | 종목코드 (상장사만 저장) |

> DART에서 하루 1회 갱신. 이후 회사 검색은 DB 조회로 처리.

---

## 서비스

### `CorpSearchService`
| 메서드 | 설명 |
|--------|------|
| `refresh` | DART에서 corp_code 목록 다운로드 → `CorpCodeCache` 전체 갱신 |
| `search` | DB에서 회사명/코드 검색. 최대 100건 반환 |

### `WatchlistService`
| 메서드 | 설명 |
|--------|------|
| `list_items` | 감시종목 목록 (즐겨찾기 → sort_order 순) |
| `create` | corp_code/srtn_cd 형식 검증 → 최대 개수 확인 → 중복 확인 → 저장 |
| `delete` | 감시종목 단건 삭제 |
| `reorder` | ID 배열 순서대로 `sort_order` 재할당 |
| `toggle_favorite` | `is_favorite` 토글 |

### `SignalRuleService`
| 메서드 | 설명 |
|--------|------|
| `get` | 설정 조회. 없으면 기본값 반환 |
| `upsert` | 설정 저장 (없으면 INSERT, 있으면 UPDATE) |

### `SignalDashboardService`
| 메서드 | 설명 |
|--------|------|
| `compute_all` | 감시종목 전체에 대해 시세+공시 병렬 조회 → 각 종목 신호 계산 → 결과 목록 반환 |

> 외부 API 호출은 `ThreadPoolExecutor(max_workers=min(len(items), 5))`로 병렬 처리.

---

## 신호 계산 로직 (`signal.py`)

### 입력
- 최신일 순 주가 데이터 배열 (`rows[0]` = 오늘)
- `SignalRuleConfig` 파라미터

### 지표 계산

| 지표 | 계산 방법 | 필요 데이터 |
|------|-----------|-------------|
| MACD | EMA(12) - EMA(26) | 최소 **35일** (26+9) |
| 시그널선 | MACD의 EMA(9) | |
| 25일 EMA 기울기 | `(EMA_now - EMA_prev) / EMA_prev * 100` | 최소 26일 |
| 거래량 비율 | `오늘 거래량 / 20일 평균` | 최소 21일 |

### 판정 규칙

```
매도 (sell) — 하나라도 해당하면 즉시 반환
  ├─ MACD 데드크로스 (MACD선이 시그널선을 하향 돌파)
  ├─ entry_price 기준 손절 구간 도달 (pct <= stop_loss_pct)
  └─ entry_price 기준 익절 구간 도달 (pct >= take_profit_pct)

매수 (buy) — 모두 충족해야 반환
  ├─ MACD 골든크로스 (MACD선이 시그널선을 상향 돌파)
  ├─ 25일 EMA 기울기 >= ema_slope_threshold
  └─ (volume_ratio_on=true일 때) 거래량 비율 >= volume_ratio_multiplier

홀딩 (hold)
  └─ 위 조건 미충족 시 hold + 미충족 이유 목록 반환
```

### MACD 상태값
| 값 | 의미 |
|----|------|
| `golden_cross` | MACD가 시그널선 상향 돌파 |
| `death_cross` | MACD가 시그널선 하향 돌파 |
| `bullish` | MACD > 시그널 (크로스 아님) |
| `bearish` | MACD < 시그널 (크로스 아님) |
| `neutral` | MACD == 시그널 |
| `None` | 데이터 부족 |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/stocks/watchlist` | 감시종목 목록 |
| POST | `/stocks/watchlist` | 감시종목 추가 |
| DELETE | `/stocks/watchlist/{id}` | 감시종목 삭제 |
| PATCH | `/stocks/watchlist/reorder` | 순서 변경 |
| PATCH | `/stocks/watchlist/{id}/favorite` | 즐겨찾기 토글 |
| GET | `/stocks/signal-rules` | 신호 규칙 조회 |
| PUT | `/stocks/signal-rules` | 신호 규칙 저장 |
| GET | `/stocks/dashboard` | 감시종목 전체 신호 계산 |
| GET | `/stocks/corp-search` | 회사명/코드 검색 |
| POST | `/stocks/corp-cache/refresh` | DART corp_code 캐시 갱신 |

---

## 외부 의존성

| 서비스 | 설명 |
|--------|------|
| 금융위원회 시세 API | 주가 데이터 (일봉). 10,000회/일, 30 TPS |
| DART API | 공시 목록 조회, corp_code 다운로드 |
| Expo Push API | 모바일 푸시 알림 발송 |

---

## 주요 규칙

- 감시종목 최대 개수: `settings.max_watch_items` (기본 10개)
- `corp_code`: 8자리 (앞에 `0` 패딩). `srtn_cd`: 6자리
- 시세 API 미설정 시 신호 계산 불가 → `hold + "시세 API 키 미설정"` 반환
- 신호 계산 결과는 `SignalEventLog`에 전량 기록
- DART corp_code 캐시는 하루 1회 갱신 권장

---

## 파일 위치

```
apps/api/app/domains/stock/
├── models.py    # WatchItem, SignalRuleConfig, StockApiUsageLog, PushToken, SignalEventLog, CorpCodeCache
├── service.py   # CorpSearchService, WatchlistService, SignalRuleService, SignalDashboardService
├── signal.py    # compute_signal (순수 도메인 로직, DB·HTTP 의존 없음)
└── schemas.py   # 요청/응답 Pydantic 스키마
apps/api/app/external/
├── stock_price.py   # 금융위원회 시세 API 클라이언트
├── dart.py          # DART API 클라이언트
├── corp_search.py   # corp_code 캐시 조회·갱신
└── disclosure.py    # 공시 감성 분류
apps/api/app/routers/
└── stocks.py
```
