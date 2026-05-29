from flight_monitor.browser import BrowserSettings


def test_browser_settings_defaults_to_persistent_humanized_profile():
    settings = BrowserSettings()

    assert settings.profile_dir.endswith("flight-monitor-profile")
    assert settings.headless is False
    assert settings.humanize is True
