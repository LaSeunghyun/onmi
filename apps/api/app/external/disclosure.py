"""공시 보고서명 기반 간이 감성 분류. 정확도 향상 시 규칙 확장 또는 모델 교체."""
from __future__ import annotations

from .dart import DartDisclosure

POSITIVE_KEYWORDS = ("실적", "증가", "호실적", "배당", "신규", "수주", "계약")
NEGATIVE_KEYWORDS = ("감소", "적자", "사기", "조사", "규제", "리콜", "소송", "지연", "부실")


def classify_sentiment(d: DartDisclosure) -> tuple[str, str]:
    """(sentiment, summary). sentiment: positive | neutral | negative."""
    name = (d.report_nm or "").strip()
    if not name:
        return "neutral", "공시명 없음"
    for k in POSITIVE_KEYWORDS:
        if k in name:
            return "positive", f"공시: {name[:50]}…" if len(name) > 50 else f"공시: {name}"
    for k in NEGATIVE_KEYWORDS:
        if k in name:
            return "negative", f"공시: {name[:50]}…" if len(name) > 50 else f"공시: {name}"
    return "neutral", f"공시: {name[:50]}…" if len(name) > 50 else f"공시: {name}"
