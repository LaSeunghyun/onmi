"""시세 API 일일 쿼터 가드. 10,000건/일, 70%/85% 도달 시 주기 확대 권장."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
DAILY_LIMIT = 10_000
THRESHOLD_70 = int(DAILY_LIMIT * 0.70)
THRESHOLD_85 = int(DAILY_LIMIT * 0.85)


def today_kst() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def recommended_interval_sec(
    used_today: int,
    num_items: int = 10,
) -> int:
    """권장 리플래시 주기(초). 1회 리플래시 = num_items 호출 가정."""
    if num_items <= 0:
        return 60
    remaining = max(0, DAILY_LIMIT - used_today)
    if used_today >= THRESHOLD_85:
        return 300
    if used_today >= THRESHOLD_70:
        return 120
    # 장중 6.5시간 = 23400초, 남은 호출로 균등 분배
    sec_per_day = 86400
    calls_possible = remaining // num_items
    if calls_possible <= 0:
        return 300
    return max(60, sec_per_day // calls_possible)
