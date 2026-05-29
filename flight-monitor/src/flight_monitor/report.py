from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from flight_monitor.runner import MonitorObservation, MonitorRunResult


def write_markdown_report(result: MonitorRunResult, path: str | Path) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_markdown_report(result), encoding="utf-8")
    return report_path


def render_markdown_report(result: MonitorRunResult) -> str:
    lines = [
        "# FareDrop Run Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]

    _append_skipped(lines, result)
    _append_errors(lines, result)
    _append_observations(lines, "Anomalies", [item for item in result.observations if item.anomaly.level != "normal"])
    _append_observations(lines, "All Captured Fares", result.observations)
    return "\n".join(lines).rstrip() + "\n"


def _append_skipped(lines: list[str], result: MonitorRunResult) -> None:
    if not result.skipped_providers:
        return
    lines.extend(["## Skipped Providers", "", "| Provider | Reason |", "| --- | --- |"])
    for provider, reason in result.skipped_providers.items():
        lines.append(f"| {_escape(provider)} | {_escape(reason)} |")
    lines.append("")


def _append_errors(lines: list[str], result: MonitorRunResult) -> None:
    if not result.errors:
        return
    lines.extend(["## Provider Errors", "", "| Provider | Route | Date | Message |", "| --- | --- | --- | --- |"])
    for error in result.errors:
        lines.append(
            f"| {_escape(error.provider)} | {_escape(error.origin)}-{_escape(error.destination)} | "
            f"{_escape(error.depart_date)} | {_escape(error.message)} |"
        )
    lines.append("")


def _append_observations(lines: list[str], title: str, observations: list[MonitorObservation]) -> None:
    lines.extend([f"## {title}", ""])
    if not observations:
        lines.extend(["None.", ""])
        return

    lines.extend(
        [
            "| Level | Provider | Route | Date | Price | Reasons | Booking URL | Screenshot |",
            "| --- | --- | --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for observation in observations:
        fare = observation.fare
        lines.append(
            f"| {_escape(observation.anomaly.level)} | {_escape(fare.provider)} | "
            f"{_escape(fare.origin)}-{_escape(fare.destination)} | {fare.depart_date.isoformat()} | "
            f"{_escape(fare.currency)} {fare.price} | {_escape(', '.join(observation.anomaly.reasons))} | "
            f"{_escape(fare.booking_url)} | {_escape(fare.screenshot_path or '')} |"
        )
    lines.append("")


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
