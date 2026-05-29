from datetime import date, datetime, timezone
from decimal import Decimal

from flight_monitor.models import FareResult
from flight_monitor.store import FareStore


def test_insert_and_read_recent_fares(tmp_path):
    store = FareStore(tmp_path / "fares.sqlite3")
    fare = FareResult(
        provider="trip",
        origin="SHA",
        destination="ICN",
        depart_date=date(2026, 7, 1),
        price=Decimal("599"),
        currency="CNY",
        booking_url="https://example.com",
        captured_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )

    store.insert_fare(fare)
    rows = store.recent_fares("SHA", "ICN", date(2026, 7, 1), limit=10)

    assert rows[0].price == Decimal("599")
    assert rows[0].provider == "trip"
