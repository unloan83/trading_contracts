from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Sequence


def liquidity_slippage_bps_per_side(turnover_inr: float) -> float:
    """Locked slippage schedule based on the instrument's prior-session turnover."""
    if turnover_inr < 0:
        raise ValueError("turnover_inr cannot be negative")
    if turnover_inr >= 5_000_000_000:
        return 1.0
    if turnover_inr >= 1_000_000_000:
        return 2.0
    if turnover_inr >= 250_000_000:
        return 4.0
    if turnover_inr >= 50_000_000:
        return 7.5
    return 12.5


def adjust_price_for_corporate_actions(
    value: float,
    on_date: date,
    actions: Sequence[Mapping[str, Any]],
    adjustment_end: date,
) -> float:
    """Back-adjust a price for actions after ``on_date`` through ``adjustment_end``."""
    adjusted = value
    for action in actions:
        ex_date = corporate_action_date(action)
        if ex_date is None or not (on_date < ex_date <= adjustment_end):
            continue
        name = str(action.get("name") or "").lower()
        if "split" in name or "bonus" in name:
            left, right = _ratio(action.get("ratio"))
            if left > 0 and right > 0:
                adjusted *= right / (left + right) if "bonus" in name else left / right
        elif "dividend" in name:
            adjusted -= float(action.get("amount") or 0.0)
    if adjusted <= 0:
        raise ValueError("corporate-action adjustment produced non-positive price")
    return adjusted


def corporate_action_date(action: Mapping[str, Any]) -> date | None:
    candidates = [action.get("expiry_date")]
    candidates.extend(
        detail.get("value") for detail in action.get("event_details", [])
        if isinstance(detail, Mapping) and "ex" in str(detail.get("name") or "").lower()
    )
    for value in candidates:
        text = str(value or "").strip()
        for fmt in ("%d %b %Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                pass
    return None


def _ratio(value: Any) -> tuple[float, float]:
    text = str(value or "").replace(" ", "")
    if ":" not in text:
        return 1.0, 1.0
    left, right = text.split(":", 1)
    try:
        return float(left), float(right)
    except ValueError:
        return 1.0, 1.0
