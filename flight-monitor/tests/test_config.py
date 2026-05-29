from datetime import date

from flight_monitor.config import load_config


def test_load_config(tmp_path):
    path = tmp_path / "routes.yaml"
    path.write_text(
        """
currency: CNY
trip_type: one_way
travelers:
  adults: 1
routes:
  - origin: SHA
    destinations: [ICN, NRT]
date_windows:
  - start: 2026-07-01
    end: 2026-07-03
providers: [trip, hopegoo, qunar]
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.currency == "CNY"
    assert config.routes[0].origin == "SHA"
    assert config.routes[0].destinations == ["ICN", "NRT"]
    assert config.date_windows[0].start == date(2026, 7, 1)
    assert config.providers == ["trip", "hopegoo", "qunar"]
