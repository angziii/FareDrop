from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from time import monotonic, sleep

from flight_monitor.models import FareResult, SearchRequest
from flight_monitor.providers.base import FlightProvider


_PRICE_RE = re.compile(r"(?:CNY|RMB|US\$|HK\$|NT\$|AU\$|CA\$|S\$|¥|￥|\$)\s?(\d[\d,]*(?:\.\d{1,2})?)")
_NON_FARE_LINE_MARKERS = ("change fee", "cancellation fee", "refund", "taxes and fees")


def parse_price_text(text: str) -> Decimal | None:
    match = _PRICE_RE.search(text.replace("\u00a0", " "))
    if not match:
        return None
    return Decimal(match.group(1).replace(",", ""))


def extract_lowest_result_price(text: str) -> Decimal | None:
    if "Depart Time" not in text:
        return None
    result_text = text.split("Depart Time", 1)[1]

    prices: list[Decimal] = []
    for raw_line in result_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if any(marker in lowered for marker in _NON_FARE_LINE_MARKERS):
            continue
        parsed = parse_price_text(line)
        if parsed:
            prices.append(parsed)
    return min(prices) if prices else None


class HopeGooProvider(FlightProvider):
    name = "hopegoo"

    def search_url(self, request: SearchRequest) -> str:
        return "https://www.hopegoo.com/"

    def search(self, page, request: SearchRequest, artifact_dir: str) -> list[FareResult]:
        artifact_path = Path(artifact_dir)
        artifact_path.mkdir(parents=True, exist_ok=True)
        page.goto(self.search_url(request), wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_load_state("load", timeout=90_000)
        self._set_currency(page, request.currency)
        self._submit_search_form(page, request)
        body_text = self._wait_for_result_text(page)

        screenshot = artifact_path / f"hopegoo-{request.origin}-{request.destination}-{request.depart_date}.png"
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

    def _set_currency(self, page, currency: str) -> None:
        requested = currency.upper()
        currency_trigger = page.locator("p[data-text]").filter(has_text=re.compile(r"^[A-Z]{3}$")).first
        try:
            current = currency_trigger.get_attribute("data-text", timeout=5_000)
            if current == requested:
                return

            currency_trigger.click()
            option = page.locator("[class*='currency-list-item']").filter(has_text=requested).first
            option.wait_for(timeout=10_000)
            option.click()

            deadline = monotonic() + 10
            while monotonic() < deadline:
                current = currency_trigger.get_attribute("data-text", timeout=2_000)
                if current == requested:
                    return
                sleep(0.5)
        except Exception:
            return

    def _submit_search_form(self, page, request: SearchRequest) -> None:
        if request.trip_type == "one_way":
            page.get_by_text("One-way", exact=True).click()
        else:
            page.get_by_text("Round-trip", exact=True).click()

        self._choose_airport(page, 0, request.origin)
        self._choose_airport(page, 1, request.destination)
        self._select_depart_date(page, request)

        page.locator("button.search").click()
        page.wait_for_load_state("domcontentloaded", timeout=90_000)

    def _choose_airport(self, page, input_index: int, code: str) -> None:
        normalized = code.upper()
        input_box = page.locator("input").nth(input_index)
        input_box.click()
        input_box.fill(normalized)

        popup = page.locator("[class*='popup-wrapper']").first
        candidate = popup.get_by_text(normalized, exact=False).first
        candidate.wait_for(timeout=15_000)
        candidate.click()

    def _select_depart_date(self, page, request: SearchRequest) -> None:
        page.locator(".project-item").nth(2).click()
        selector = f".day[data-val='{request.depart_date.isoformat()}'][data-enable='true']"

        for _ in range(18):
            target = page.locator(selector)
            if target.count():
                target.first.click()
                return
            page.locator(".cal_btn_next").first.click()
            sleep(0.5)

        raise TimeoutError(f"HopeGoo date is not selectable: {request.depart_date.isoformat()}")

    def _wait_for_result_text(self, page, timeout_seconds: int = 60) -> str:
        deadline = monotonic() + timeout_seconds
        last_text = ""
        while monotonic() < deadline:
            last_text = page.locator("body").inner_text(timeout=10_000)
            if extract_lowest_result_price(last_text) is not None:
                return last_text
            sleep(2)
        return last_text
