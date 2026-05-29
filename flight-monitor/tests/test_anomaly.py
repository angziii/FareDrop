from datetime import date, datetime, timezone
from decimal import Decimal

from flight_monitor.anomaly import classify_fare
from flight_monitor.models import FareResult


def fare(price: str, provider: str = "trip") -> FareResult:
    return FareResult(
        provider=provider,
        origin="SHA",
        destination="ICN",
        depart_date=date(2026, 7, 1),
        price=Decimal(price),
        currency="CNY",
        booking_url="https://example.com",
        captured_at=datetime.now(timezone.utc),
    )


def test_flags_strong_possible_mistake_fare_against_history_and_peers():
    result = classify_fare(
        fare("450"),
        historical=[fare("1200"), fare("1300"), fare("1100")],
        peers=[fare("1500", "hopegoo")],
    )

    assert result.level == "strong"
    assert "historical_median" in result.reasons
    assert "peer_min" in result.reasons


def test_does_not_flag_normal_low_price():
    result = classify_fare(
        fare("950"),
        historical=[fare("1000"), fare("1050"), fare("980")],
        peers=[fare("970", "hopegoo")],
    )

    assert result.level == "normal"
