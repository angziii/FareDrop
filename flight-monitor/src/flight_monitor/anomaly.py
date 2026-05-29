from __future__ import annotations

from decimal import Decimal
from statistics import median
from typing import Literal

from pydantic import BaseModel

from flight_monitor.models import FareResult


AnomalyLevel = Literal["normal", "watch", "strong"]


class AnomalyResult(BaseModel):
    level: AnomalyLevel
    reasons: list[str]


def classify_fare(fare: FareResult, historical: list[FareResult], peers: list[FareResult]) -> AnomalyResult:
    reasons: list[str] = []
    level: AnomalyLevel = "normal"

    history_prices = [item.price for item in historical if item.price > 0]
    if len(history_prices) >= 3:
        historical_median = Decimal(str(median(history_prices)))
        if fare.price <= historical_median * Decimal("0.60"):
            reasons.append("historical_median")
            level = "strong"
        elif fare.price <= historical_median * Decimal("0.75"):
            reasons.append("historical_median")
            level = "watch"

    peer_prices = [item.price for item in peers if item.provider != fare.provider and item.price > 0]
    if peer_prices:
        peer_min = min(peer_prices)
        if fare.price <= peer_min * Decimal("0.70"):
            reasons.append("peer_min")
            level = "strong"
        elif fare.price <= peer_min * Decimal("0.85") and level == "normal":
            reasons.append("peer_min")
            level = "watch"

    if fare.price <= Decimal("300"):
        reasons.append("absolute_floor")
        level = "strong"

    return AnomalyResult(level=level, reasons=reasons)
