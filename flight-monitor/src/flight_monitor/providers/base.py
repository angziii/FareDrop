from __future__ import annotations

from abc import ABC, abstractmethod

from flight_monitor.models import FareResult, SearchRequest


class FlightProvider(ABC):
    name = "base"

    @abstractmethod
    def search(self, page, request: SearchRequest, artifact_dir: str) -> list[FareResult]:
        """Return normalized fare results for one search request."""
        raise NotImplementedError
