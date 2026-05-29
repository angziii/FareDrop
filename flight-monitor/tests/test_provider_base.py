from flight_monitor.providers.base import FlightProvider


def test_provider_interface_has_name():
    assert FlightProvider.name == "base"
