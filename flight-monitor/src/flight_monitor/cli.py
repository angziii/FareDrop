from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from flight_monitor.browser import BrowserSettings
from flight_monitor.config import load_config
from flight_monitor.report import write_markdown_report
from flight_monitor.runner import MonitorRunResult, run_monitor
from flight_monitor.store import FareStore


console = Console()


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("flight-monitor/config/routes.example.yaml"),
    show_default=True,
    help="Route/date matrix YAML file.",
)
@click.option(
    "--db",
    "db_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("data/fares.sqlite3"),
    show_default=True,
    help="SQLite fare history database.",
)
@click.option(
    "--artifacts",
    "artifact_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/artifacts"),
    show_default=True,
    help="Screenshot artifact directory.",
)
@click.option(
    "--profile",
    "profile_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("data/flight-monitor-profile"),
    show_default=True,
    help="Persistent CloakBrowser profile directory.",
)
@click.option(
    "--report",
    "report_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("data/latest-report.md"),
    show_default=True,
    help="Markdown run report path.",
)
@click.option("--max-requests", type=int, default=None, help="Limit expanded route/date requests for smoke runs.")
@click.option("--headless/--headed", default=False, show_default=True, help="Run browser without a visible window.")
def main(
    config_path: Path,
    db_path: Path,
    artifact_dir: Path,
    profile_dir: Path,
    report_path: Path,
    max_requests: int | None,
    headless: bool,
) -> None:
    config = load_config(config_path)
    store = FareStore(db_path)
    result = run_monitor(
        config=config,
        store=store,
        browser_settings=BrowserSettings(profile_dir=str(profile_dir), headless=headless),
        artifact_dir=str(artifact_dir),
        max_requests=max_requests,
    )
    written_report = write_markdown_report(result, report_path)
    _render_result(result)
    console.print(f"Report written to {written_report}")


def _render_result(result: MonitorRunResult) -> None:
    for provider, reason in result.skipped_providers.items():
        console.print(f"[yellow]Skipped {provider}:[/yellow] {reason}")

    if result.errors:
        error_table = Table(title="Provider Errors")
        error_table.add_column("Provider")
        error_table.add_column("Route")
        error_table.add_column("Date")
        error_table.add_column("Message")
        for error in result.errors:
            error_table.add_row(
                error.provider,
                f"{error.origin}-{error.destination}",
                error.depart_date,
                error.message[:120],
            )
        console.print(error_table)

    if not result.observations:
        console.print("[yellow]No fares captured.[/yellow]")
        return

    fare_table = Table(title="Captured Fares")
    fare_table.add_column("Level")
    fare_table.add_column("Provider")
    fare_table.add_column("Route")
    fare_table.add_column("Date")
    fare_table.add_column("Price", justify="right")
    fare_table.add_column("Reasons")
    for observation in result.observations:
        fare = observation.fare
        fare_table.add_row(
            observation.anomaly.level,
            fare.provider,
            f"{fare.origin}-{fare.destination}",
            fare.depart_date.isoformat(),
            f"{fare.currency} {fare.price}",
            ", ".join(observation.anomaly.reasons),
        )
    console.print(fare_table)


if __name__ == "__main__":
    main()
