"""규칙 기반 매수/매도/홀딩 신호. PRD 규칙 스펙 반영."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .stock_price import StockPriceRow


@dataclass
class SignalResult:
    signal: str  # buy | sell | hold
    reasons: list[str]
    macd_state: str | None
    ema25_slope: float | None
    volume_ratio: float | None


def _ema(prices: list[float], period: int) -> float | None:
    if len(prices) < period or period <= 0:
        return None
    k = 2.0 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = p * k + ema * (1 - k)
    return ema


def _macd_values(closes: list[float], fast: int = 12, slow: int = 26, signal_period: int = 9) -> tuple[list[float], list[float]]:
    """rows는 최신순(0=오늘). 과거→현재 순으로 MACD·시그널 계산 후 [최신, ...] 반환."""
    if len(closes) < slow + signal_period:
        return [], []
    chrono = closes[::-1]
    macd_chrono: list[float] = []
    for i in range(slow - 1, len(chrono)):
        w = chrono[i - (slow - 1) : i + 1]
        e12 = _ema(w, fast)
        e26 = _ema(w, slow)
        macd_chrono.append((e12 - e26) if (e12 is not None and e26 is not None) else 0.0)
    if len(macd_chrono) < signal_period:
        return [], []
    signal_chrono: list[float] = []
    for i in range(signal_period - 1, len(macd_chrono)):
        w = macd_chrono[i - (signal_period - 1) : i + 1]
        s = _ema(w, signal_period)
        signal_chrono.append(s if s is not None else 0.0)
    macd_newest_first = list(reversed(macd_chrono[signal_period - 1 :]))
    signal_newest_first = list(reversed(signal_chrono))
    return macd_newest_first, signal_newest_first


# MACD(EMA26) + 시그널(EMA9) 계산에 최소 26+9=35일 종가 필요
MACD_MIN_DAYS = 35


def _macd_signal(rows: list[StockPriceRow]) -> tuple[str | None, bool]:
    """(macd_state, golden_cross). 골든크로스=MACD선이 시그널선을 상향 돌파."""
    closes = [float(r.close) for r in rows if r.close is not None]
    if len(closes) < MACD_MIN_DAYS:
        return None, False
    macd_list, signal_list = _macd_values(closes)
    if len(macd_list) < 2 or len(signal_list) < 2:
        return "neutral", False
    macd_now = macd_list[0]
    signal_now = signal_list[0]
    macd_prev = macd_list[1]
    signal_prev = signal_list[1]
    if macd_prev <= signal_prev and macd_now > signal_now:
        return "golden_cross", True
    if macd_prev >= signal_prev and macd_now < signal_now:
        return "death_cross", False
    if macd_now > signal_now:
        return "bullish", False
    if macd_now < signal_now:
        return "bearish", False
    return "neutral", False


def _ema25_slope(rows: list[StockPriceRow]) -> float | None:
    closes = [r.close for r in rows if r.close is not None]
    if len(closes) < 26:
        return None
    ema_now = _ema(closes, 25)
    ema_prev = _ema(closes[:-1], 25)
    if ema_now is None or ema_prev is None or ema_prev == 0:
        return None
    return (ema_now - ema_prev) / ema_prev * 100


def _volume_ratio(rows: list[StockPriceRow], multiplier: float = 1.5) -> float | None:
    if len(rows) < 21:
        return None
    vols = [r.volume for r in rows if r.volume is not None]
    if len(vols) < 20:
        return None
    avg20 = sum(vols[:20]) / 20
    if avg20 == 0:
        return None
    return vols[0] / avg20


def compute_signal(
    rows: list[StockPriceRow],
    *,
    stop_loss_pct: float | None = None,
    take_profit_pct: float | None = None,
    ema_slope_threshold: float = 0.0,
    volume_ratio_on: bool = True,
    volume_ratio_multiplier: float = 1.5,
    entry_price: float | None = None,
) -> SignalResult:
    """매수/매도/홀딩 판정. rows는 최신일 순(인덱스 0이 최신)."""
    reasons: list[str] = []
    if not rows:
        return SignalResult("hold", ["데이터 없음"], None, None, None)

    macd_state, golden_cross = _macd_signal(rows)
    ema_slope = _ema25_slope(rows)
    vol_ratio = _volume_ratio(rows, volume_ratio_multiplier)

    current = rows[0].close
    if current is None:
        return SignalResult("hold", ["종가 없음"], macd_state, ema_slope, vol_ratio)

    # 매도: 데드크로스 또는 퍼센트
    if macd_state == "death_cross":
        reasons.append("MACD 데드크로스")
    if entry_price and entry_price > 0:
        pct = (current - entry_price) / entry_price * 100
        if stop_loss_pct is not None and pct <= stop_loss_pct:
            reasons.append(f"손절 구간 도달 ({pct:.1f}%)")
        if take_profit_pct is not None and pct >= take_profit_pct:
            reasons.append(f"익절 구간 도달 ({pct:.1f}%)")

    if reasons:
        return SignalResult("sell", reasons, macd_state, ema_slope, vol_ratio)

    # 매수: 골든크로스 + EMA 기울기 + (옵션) 거래량
    if golden_cross and ema_slope is not None and ema_slope >= ema_slope_threshold:
        vol_ok = not volume_ratio_on or (vol_ratio is not None and vol_ratio >= volume_ratio_multiplier)
        if vol_ok:
            reasons.append("MACD 상승 전환(골든크로스)")
            if ema_slope is not None:
                reasons.append(f"25일 EMA 기울기 충족 ({ema_slope:.2f}%)")
            if volume_ratio_on and vol_ratio is not None:
                reasons.append(f"거래량 조건 충족 ({vol_ratio:.1f}배)")
            return SignalResult("buy", reasons, macd_state, ema_slope, vol_ratio)

    hold_reasons: list[str] = []
    if not golden_cross:
        hold_reasons.append(f"MACD 골든크로스 미발생(현재:{macd_state or '계산불가'})")
    if ema_slope is not None and ema_slope < ema_slope_threshold:
        hold_reasons.append(f"25일 EMA 기울기 {ema_slope:.2f}%(기준 {ema_slope_threshold}% 미만)")
    if volume_ratio_on and vol_ratio is not None and vol_ratio < volume_ratio_multiplier:
        hold_reasons.append(f"거래량 {vol_ratio:.1f}배(기준 {volume_ratio_multiplier}배 미만)")
    if not hold_reasons:
        hold_reasons.append("매수 조건 일부 미충족")
    return SignalResult("hold", hold_reasons, macd_state, ema_slope, vol_ratio)
