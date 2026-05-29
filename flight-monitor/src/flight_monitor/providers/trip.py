from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urlencode

from flight_monitor.models import FareResult, SearchRequest
from flight_monitor.providers.base import FlightProvider


def parse_price_text(text: str) -> Decimal | None:
    match = re.search(r"(\d[\d,]*)", text.replace("\u00a0", " "))
    if not match:
        return None
    return Decimal(match.group(1).replace(",", ""))


def extract_lowest_result_price(text: str) -> Decimal | None:
    result_text = text
    if "Departing for" in result_text:
        result_text = result_text.split("Departing for", 1)[1]
    if "Price alerts" in result_text:
        result_text = result_text.split("Price alerts", 1)[0]

    prices: list[Decimal] = []
    for raw in re.findall(r"(?:¥|CNY|RMB)\s?[\d,]+", result_text):
        parsed = parse_price_text(raw)
        if parsed:
            prices.append(parsed)
    return min(prices) if prices else None


class TripProvider(FlightProvider):
    name = "trip"

    def search_url(self, request: SearchRequest) -> str:
        params = urlencode(
            {
                "locale": "zh-CN",
                "curr": request.currency,
                "dcity": request.origin,
                "acity": request.destination,
                "ddate": request.depart_date.isoformat(),
                "triptype": "ow",
            }
        )
        return f"https://www.trip.com/flights/?{params}"

    def search(self, page, request: SearchRequest, artifact_dir: str) -> list[FareResult]:
        artifact_path = Path(artifact_dir)
        artifact_path.mkdir(parents=True, exist_ok=True)

        page.goto(self.search_url(request), wait_until="load", timeout=90_000)
        sleep(2)
        self._submit_search_form(page, request)
        body_text = self._wait_for_result_text(page)

        screenshot = artifact_path / f"trip-{request.origin}-{request.destination}-{request.depart_date}.png"
        page.screenshot(path=str(screenshot), full_page=True)

        price = extract_lowest_result_price(body_text)

        if price is None:
            return []

        return [
            FareResult(
                provider=self.name,
                origin=request.origin,
                destination=request.destination,
                depart_date=request.depart_date,
                return_date=request.return_date,
                price=price,
                currency=request.currency,
                booking_url=page.url,
                screenshot_path=str(screenshot),
                captured_at=datetime.now(timezone.utc),
            )
        ]

    def _submit_search_form(self, page, request: SearchRequest) -> None:
        destination_input = page.get_by_test_id("search_city_to0").first
        destination_input.click()
        destination_input.fill(request.destination.upper())

        result_box = page.get_by_test_id("search_result_box")
        result_box.get_by_text(request.destination.upper()).first.wait_for(timeout=15_000)
        result_box.locator("[role='button']").first.click()

        search_button = page.get_by_test_id("search_btn")
        search_button.click()
        page.wait_for_load_state("load", timeout=90_000)

    def _wait_for_result_text(self, page, timeout_seconds: int = 45) -> str:
        deadline = monotonic() + timeout_seconds
        last_text = ""
        while monotonic() < deadline:
            last_text = page.locator("body").inner_text(timeout=10_000)
            if extract_lowest_result_price(last_text) is not None:
                return last_text
            sleep(2)
        return last_text
