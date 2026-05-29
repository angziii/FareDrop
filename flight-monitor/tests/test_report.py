from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from flight_monitor.anomaly import AnomalyResult
from flight_monitor.models import FareResult
from flight_monitor.report import render_markdown_report, write_markdown_report
from flight_monitor.runner import MonitorObservation, MonitorRunResult


def test_render_markdown_report_includes_anomalies_and_skipped_providers():
    fare = FareResult(
        provider="trip",
        origin="SHA",
        destination="CAN",
        depart_date=date(2026, 7, 1),
        price=Decimal("299"),
        currency="CNY",
        booking_url="https://example.com",
        screenshot_path="data/artifacts/trip.png",
        captured_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    result = MonitorRunResult(
        observations=[
            MonitorObservation(
                fare=fare,
                anomaly=AnomalyResult(level="strong", reasons=["absolute_floor"]),
            )
        ],
        skipped_providers={"qunar": "login-free result list unavailable"},
        errors=[],
    )

    markdown = render_markdown_report(result)

    assert "## Skipped Providers" in markdown
    assert "qunar" in markdown
    assert "## Anomalies" in markdown
    assert "CNY 299" in markdown
    assert "absolute_floor" in markdown


def test_write_markdown_report_creates_parent_directory(tmp_path):
    result = MonitorRunResult(observations=[], skipped_providers={}, errors=[])
    path = write_markdown_report(result, tmp_path / "nested" / "report.md")

    assert path.exists()
    assert "All Captured Fares" in path.read_text(encoding="utf-8")
