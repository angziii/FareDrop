from datetime import date

from flight_monitor.matrix import build_search_requests
from flight_monitor.models import DateWindow, MonitorConfig, RouteSpec, Travelers


def test_build_search_requests_expands_routes_and_dates():
    config = MonitorConfig(
        currency="CNY",
        trip_type="one_way",
        travelers=Travelers(adults=1),
        routes=[RouteSpec(origin="SHA", destinations=["ICN", "NRT"])],
        date_windows=[DateWindow(start=date(2026, 7, 1), end=date(2026, 7, 2))],
        providers=["trip"],
    )

    requests = build_search_requests(config)

    assert [(r.origin, r.destination, r.depart_date.isoformat()) for r in requests] == [
        ("SHA", "ICN", "2026-07-01"),
        ("SHA", "ICN", "2026-07-02"),
        ("SHA", "NRT", "2026-07-01"),
        ("SHA", "NRT", "2026-07-02"),
    ]
