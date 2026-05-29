from datetime import date

from flight_monitor.browser import BrowserSettings, launch_monitor_context
from flight_monitor.models import SearchRequest
from flight_monitor.providers.trip import TripProvider


ctx = launch_monitor_context(BrowserSettings())
page = ctx.new_page()
result = TripProvider().search(
    page,
    SearchRequest(origin="SHA", destination="ICN", depart_date=date(2026, 7, 1), currency="CNY"),
    "data/artifacts",
)
print(result)
ctx.close()
