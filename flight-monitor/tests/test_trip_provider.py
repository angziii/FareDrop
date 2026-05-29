from datetime import date
from decimal import Decimal

from flight_monitor.models import SearchRequest
from flight_monitor.providers.trip import TripProvider, extract_lowest_result_price, parse_price_text


def test_trip_search_url_contains_route_and_date():
    provider = TripProvider()
    request = SearchRequest(origin="SHA", destination="ICN", depart_date=date(2026, 7, 1))

    url = provider.search_url(request)

    assert "trip.com/flights" in url
    assert "SHA" in url.upper()
    assert "ICN" in url.upper()
    assert "2026-07-01" in url


def test_parse_price_text():
    assert parse_price_text("¥1,234") == Decimal("1234")
    assert parse_price_text("CNY 599") == Decimal("599")


def test_extract_lowest_result_price_ignores_calendar_and_alert_prices():
    text = """
Wed, Jul 1
CNY 842
Departing for Seoul
153 flights found
Cheapest
CNY 1,000
Eastar Jet
CNY 1,050
Price alerts
Recommended: CNY 969
"""

    assert extract_lowest_result_price(text) == Decimal("1000")
