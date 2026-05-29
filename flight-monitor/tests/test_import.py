def test_import_package():
    import flight_monitor

    assert flight_monitor.__version__ == "0.1.0"
