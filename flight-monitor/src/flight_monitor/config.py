from __future__ import annotations

from pathlib import Path

import yaml

from flight_monitor.models import MonitorConfig


def load_config(path: str | Path) -> MonitorConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return MonitorConfig.model_validate(data)
