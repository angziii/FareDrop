from __future__ import annotations

from datetime import timedelta

from flight_monitor.models import MonitorConfig, SearchRequest


def build_search_requests(config: MonitorConfig) -> list[SearchRequest]:
    requests: list[SearchRequest] = []
    for route in config.routes:
        for destination in route.destinations:
            for window in config.date_windows:
                current = window.start
                while current <= window.end:
                    requests.append(
                        SearchRequest(
                            origin=route.origin,
                            destination=destination,
                            depart_date=current,
                            currency=config.currency,
                            adults=config.travelers.adults,
                            trip_type=config.trip_type,
                        )
                    )
                    current += timedelta(days=1)
    return requests
