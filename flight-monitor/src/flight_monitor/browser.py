from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cloakbrowser import launch_persistent_context


@dataclass(frozen=True)
class BrowserSettings:
    profile_dir: str = "data/flight-monitor-profile"
    headless: bool = False
    humanize: bool = True
    locale: str = "zh-CN"
    timezone: str = "Asia/Shanghai"


def launch_monitor_context(settings: BrowserSettings) -> Any:
    Path(settings.profile_dir).mkdir(parents=True, exist_ok=True)
    return launch_persistent_context(
        settings.profile_dir,
        headless=settings.headless,
        humanize=settings.humanize,
        locale=settings.locale,
        timezone=settings.timezone,
    )
