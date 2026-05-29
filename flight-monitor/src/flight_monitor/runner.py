from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from flight_monitor.anomaly import AnomalyResult, classify_fare
from flight_monitor.browser import BrowserSettings, launch_monitor_context
from flight_monitor.matrix import build_search_requests
from flight_monitor.models import FareResult, MonitorConfig, ProviderName
from flight_monitor.providers.base import FlightProvider
from flight_monitor.providers.registry import SKIPPED_PROVIDER_REASONS, build_provider
from flight_monitor.store import FareStore


ProviderFactory = Callable[[ProviderName], FlightProvider | None]
ContextFactory = Callable[[BrowserSettings], Any]


@dataclass(frozen=True)
class MonitorObservation:
    fare: FareResult
    anomaly: AnomalyResult


@dataclass(frozen=True)
class ProviderError:
    provider: ProviderName
    origin: str
    destination: str
    depart_date: str
    message: str


@dataclass(frozen=True)
class MonitorRunResult:
    observations: list[MonitorObservation]
    skipped_providers: dict[ProviderName, str]
    errors: list[ProviderError]


def run_monitor(
    config: MonitorConfig,
    store: FareStore,
    browser_settings: BrowserSettings | None = None,
    artifact_dir: str = "data/artifacts",
    max_requests: int | None = None,
    provider_factory: ProviderFactory = build_provider,
    context_factory: ContextFactory = launch_monitor_context,
) -> MonitorRunResult:
    settings = browser_settings or BrowserSettings()
    requests = build_search_requests(config)
    if max_requests is not None:
        requests = requests[:max_requests]
    providers: dict[ProviderName, FlightProvider] = {}
    skipped: dict[ProviderName, str] = {}

    for name in config.providers:
        provider = provider_factory(name)
        if provider is None:
            skipped[name] = SKIPPED_PROVIDER_REASONS.get(name, "Provider is not implemented.")
            continue
        providers[name] = provider

    observations: list[MonitorObservation] = []
    errors: list[ProviderError] = []
    if not providers or not requests:
        return MonitorRunResult(observations=observations, skipped_providers=skipped, errors=errors)

    context = context_factory(settings)
    try:
        page = context.new_page()
        for request in requests:
            historical = store.recent_fares(request.origin, request.destination, request.depart_date, limit=30)
            current_fares: list[FareResult] = []

            for name, provider in providers.items():
                try:
                    current_fares.extend(provider.search(page, request, artifact_dir))
                except Exception as exc:
                    errors.append(
                        ProviderError(
                            provider=name,
                            origin=request.origin,
                            destination=request.destination,
                            depart_date=request.depart_date.isoformat(),
                            message=str(exc),
                        )
                    )

            for fare in current_fares:
                store.insert_fare(fare)
                anomaly = classify_fare(
                    fare,
                    historical=historical,
                    peers=[peer for peer in current_fares if peer.provider != fare.provider],
                )
                observations.append(MonitorObservation(fare=fare, anomaly=anomaly))
    finally:
        context.close()

    return MonitorRunResult(observations=observations, skipped_providers=skipped, errors=errors)
