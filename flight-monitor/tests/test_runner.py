from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from flight_monitor.models import DateWindow, FareResult, MonitorConfig, RouteSpec
from flight_monitor.runner import run_monitor
from flight_monitor.store import FareStore


class FakeProvider:
    name = "trip"

    def search(self, page, request, artifact_dir):
        assert page == "page"
        assert artifact_dir == "artifacts"
        return [
            FareResult(
                provider=self.name,
                origin=request.origin,
                destination=request.destination,
                depart_date=request.depart_date,
                price=Decimal("299"),
                currency=request.currency,
                booking_url="https://example.com",
                captured_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
            )
        ]


class FakeContext:
    def __init__(self):
        self.closed = False

    def new_page(self):
        return "page"

    def close(self):
        self.closed = True


def test_run_monitor_captures_fares_and_skips_unsupported_provider(tmp_path):
    context = FakeContext()
    config = MonitorConfig(
        routes=[RouteSpec(origin="SHA", destinations=["CAN"])],
        date_windows=[DateWindow(start=date(2026, 7, 1), end=date(2026, 7, 1))],
        providers=["trip", "qunar"],
    )
    store = FareStore(tmp_path / "fares.sqlite3")

    result = run_monitor(
        config=config,
        store=store,
        artifact_dir="artifacts",
        provider_factory=lambda name: FakeProvider() if name == "trip" else None,
        context_factory=lambda settings: context,
    )

    assert context.closed is True
    assert result.skipped_providers["qunar"]
    assert result.observations[0].fare.price == Decimal("299")
    assert result.observations[0].anomaly.level == "strong"
    assert store.all_fares()[0].price == Decimal("299")


def test_run_monitor_can_limit_expanded_requests(tmp_path):
    context = FakeContext()
    config = MonitorConfig(
        routes=[RouteSpec(origin="SHA", destinations=["CAN"])],
        date_windows=[DateWindow(start=date(2026, 7, 1), end=date(2026, 7, 3))],
        providers=["trip"],
    )
    store = FareStore(tmp_path / "fares.sqlite3")

    result = run_monitor(
        config=config,
        store=store,
        artifact_dir="artifacts",
        max_requests=1,
        provider_factory=lambda name: FakeProvider(),
        context_factory=lambda settings: context,
    )

    assert len(result.observations) == 1
    assert result.observations[0].fare.depart_date == date(2026, 7, 1)
