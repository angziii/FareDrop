from __future__ import annotations

from flight_monitor.models import ProviderName
from flight_monitor.providers.base import FlightProvider
from flight_monitor.providers.hopegoo import HopeGooProvider
from flight_monitor.providers.trip import TripProvider


SUPPORTED_PROVIDERS: tuple[ProviderName, ...] = ("trip", "hopegoo")
SKIPPED_PROVIDER_REASONS: dict[ProviderName, str] = {
    "qunar": "Qunar is deferred because the current public paths do not expose a reliable login-free result list.",
}


def build_provider(name: ProviderName) -> FlightProvider | None:
    if name == "trip":
        return TripProvider()
    if name == "hopegoo":
        return HopeGooProvider()
    return None
