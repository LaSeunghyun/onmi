# Content 도메인

키워드 기반 뉴스 수집·처리·리포트를 담당하는 도메인.

---

## 역할

- 사용자가 등록한 키워드 관리 (CRUD)
- 키워드 매칭 기사 수집 (검색 API / RSS)
- 수집된 기사 처리 파이프라인 실행 (감성 분석 → 요약 → 번역)
- 일일 알림 설정 관리

---

## 모델

### `Keyword`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User) | |
| `text` | str (index) | 공백 정규화 후 저장 |
| `is_active` | bool | 비활성화 시 수집 제외 |
| `is_pinned` | bool | 고정 키워드 여부 |
| `last_used_at` | datetime? | 최근 수집 시각 |
| `created_at` | datetime | |
| `updated_at` | datetime | |

> 동일 user_id + text 조합은 유니크 (`409` 반환)

### `Article`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User) | |
| `date_kst` | str | `YYYY-MM-DD` 형식, 수집 날짜 (KST) |
| `canonical_url` | str (index) | 중복 제거용 정규화 URL |
| `original_url` | str | 원본 URL |
| `source_type` | str | `search_api` \| `rss` |
| `source_name` | str? | 언론사명 등 |
| `published_at` | datetime? | 기사 발행 시각 |
| `fetched_at` | datetime | 수집 시각 |
| `title_original` | str | 원문 제목 |
| `snippet_original` | str? | 원문 발췌 |
| `language_original` | str? | 감지된 원문 언어 코드 |

> user_id + canonical_url 조합은 유니크 → 동일 기사 중복 수집 방지

### `ArticleKeyword`
| 필드 | 타입 | 설명 |
|------|------|------|
| `article_id` | UUID (FK → Article) | |
| `keyword_id` | UUID (FK → Keyword) | |

> Article ↔ Keyword 다대다 관계 테이블. article_id + keyword_id 유니크.

### `ProcessingResult`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User) | |
| `article_id` | UUID (FK → Article, unique) | 1:1 관계 |
| `sentiment` | str | `positive` \| `neutral` \| `negative` |
| `sentiment_confidence` | float? | 감성 분류 신뢰도 |
| `summary_original` | str | 원문 요약 |
| `summary_ko` | str | 한국어 요약 |
| `translated_from` | str? | 번역 원본 언어 코드 |
| `translation_status` | str | `not_needed` \| `completed` \| `failed` |
| `created_at` | datetime | |

### `NotificationSetting`
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User, unique) | 1:1 관계 |
| `daily_report_time_hhmm` | str | 기본값 `"09:00"` |
| `is_enabled` | bool | 알림 활성 여부 |
| `updated_at` | datetime | |

---

## 서비스 (`KeywordService`)

| 메서드 | 설명 |
|--------|------|
| `list_keywords` | 필터(all/active/inactive), 검색(q), 정렬(pinned_recent/recent/alpha) 지원 |
| `create` | 텍스트 공백 정규화 → 중복 검사 → 저장 |
| `update` | `is_active`, `is_pinned` 변경. 변경 여부와 변경 전 스냅샷 반환 (감사 로그용) |
| `delete` | 삭제 후 `(deleted_id, deleted_text)` 반환 (감사 로그용) |

---

## 처리 파이프라인

```
수집 (collect)
  └─ 키워드별 검색 API / RSS 조회
  └─ canonical_url로 중복 제거
  └─ Article + ArticleKeyword 저장

처리 (process)
  └─ 감성 분석 → sentiment, sentiment_confidence
  └─ 원문 요약 → summary_original
  └─ 한국어 번역/요약 → summary_ko, translation_status
  └─ ProcessingResult 저장
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/keywords` | 키워드 목록 (`q`, `status`, `sort` 쿼리 파라미터) |
| POST | `/keywords` | 키워드 생성 |
| PATCH | `/keywords/{id}` | 키워드 수정 (is_active, is_pinned) |
| DELETE | `/keywords/{id}` | 키워드 삭제 |
| GET | `/articles` | 기사 목록 조회 |
| POST | `/collect` | 기사 수집 트리거 |
| POST | `/process` | 기사 처리 트리거 (요약·번역·감성) |
| GET | `/report` | 일일 리포트 조회 |
| GET/PUT | `/settings` | 알림 설정 조회·수정 |

---

## 주요 규칙

- 키워드 텍스트: `" ".join(text.strip().split())` 으로 연속 공백 제거 후 저장
- 동일 키워드 중복 등록 시 `409` 반환
- 기사 중복 수집 방지: `canonical_url` 기준 (user 범위)
- `ProcessingResult`는 article당 1개 (`article_id` unique)
- 알림 설정은 user당 1개 (`user_id` unique)

---

## 파일 위치

```
apps/api/app/domains/content/
├── models.py    # Keyword, Article, ArticleKeyword, ProcessingResult, NotificationSetting
├── service.py   # KeywordService
└── schemas.py   # 요청/응답 Pydantic 스키마
apps/api/app/
├── collect.py   # 수집 오케스트레이션
└── process.py   # 처리 파이프라인
apps/api/app/routers/
├── keywords.py
├── articles.py
├── collect.py
├── process.py
├── report.py
└── settings.py
```
