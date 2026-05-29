from datetime import date
from decimal import Decimal

from flight_monitor.models import SearchRequest
from flight_monitor.providers.hopegoo import HopeGooProvider, extract_lowest_result_price, parse_price_text


def test_hopegoo_url_uses_site_entry():
    provider = HopeGooProvider()
    request = SearchRequest(origin="SHA", destination="ICN", depart_date=date(2026, 7, 1))

    assert provider.search_url(request).startswith("https://www.hopegoo.com/")


def test_parse_price_text():
    assert parse_price_text("¥688") == Decimal("688")
    assert parse_price_text("CNY 1,088") == Decimal("1088")
    assert parse_price_text("US$ 144.94") == Decimal("144.94")
    assert parse_price_text("￥979") == Decimal("979")


def test_extract_lowest_result_price_ignores_calendar_and_fee_amounts():
    text = """
6-30 Tue
￥812
Price Calendar
Depart
(Shanghai To Seoul | Wed, Jul 1)
100 results
Depart Time
ArrivalTime
Duration
Price
Cathay Pacific
￥979
Economy
Change fee：from ¥810
Cancellation fee：from ¥400
Eastar Jet
￥1,062
Book
"""

    assert extract_lowest_result_price(text) == Decimal("979")


def test_extract_lowest_result_price_ignores_homepage_coupon_prices():
    text = """
New User Discount
CNY 22.9 OFF
Flight Promotion
Popular Cheap Flights
Hong KongShanghai
CNY 605
"""

    assert extract_lowest_result_price(text) is None
