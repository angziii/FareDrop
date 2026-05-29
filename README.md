# FareDrop

FareDrop is a local low-fare flight monitor focused on China-friendly booking platforms. It uses CloakBrowser-powered browser automation to search configured route and date matrices, store the cheapest visible fares, and flag unusually low prices for manual review.

This repository is no longer presented as a CloakBrowser fork. CloakBrowser remains included as the browser automation foundation, but the project direction here is FareDrop: a flight price monitoring tool for Trip.com, HopeGoo, and other domestic or China-focused platforms.

## Current Status

- Trip.com and HopeGoo providers are implemented and smoke-tested.
- Qunar is intentionally not enabled because current search paths either surface login/App prompts or do not expose a usable public result list reliably.
- Route/date matrix configuration is YAML-based.
- Fare history is stored in SQLite.
- Basic anomaly rules flag possible mistake fares.
- Browser sessions use persistent CloakBrowser profiles with Chinese locale and Asia/Shanghai timezone defaults.

## Fare Scope

FareDrop currently searches for the cheapest available fare unless a provider is explicitly configured otherwise. The Trip.com provider does **not** enable the nonstop-only filter, so results include both nonstop and connecting flights. This matches the current product goal: find the lowest price first, then let a human decide whether the itinerary is acceptable.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pip install -e "./flight-monitor[dev]"
python -m cloakbrowser install
```

Run the current test suite:

```bash
PYTHONPATH="$PWD/flight-monitor/src:$PWD" .venv/bin/python -m pytest flight-monitor/tests -q
```

Run provider smoke checks:

```bash
PYTHONPATH="$PWD/flight-monitor/src:$PWD" .venv/bin/python flight-monitor/manual/trip_smoke.py
PYTHONPATH="$PWD/flight-monitor/src:$PWD" .venv/bin/python flight-monitor/manual/hopegoo_smoke.py
```

The smoke check opens a visible browser, saves screenshots under `data/artifacts/`, and prints normalized fare rows.

## Configuration

Example route matrix:

```yaml
currency: CNY
trip_type: one_way
travelers:
  adults: 1
routes:
  - origin: SHA
    destinations: [ICN, NRT, BKK]
  - origin: CAN
    destinations: [SIN, KUL]
date_windows:
  - start: 2026-07-01
    end: 2026-07-31
providers: [trip, hopegoo]
```

The example file lives at `flight-monitor/config/routes.example.yaml`.

## Project Layout

```text
flight-monitor/
  config/                 example route matrices
  manual/                 provider smoke scripts
  src/flight_monitor/     FareDrop implementation
  tests/                  unit tests
cloakbrowser/             CloakBrowser Python package used by FareDrop
js/                       upstream CloakBrowser JavaScript package
```

## Attribution

FareDrop builds on CloakBrowser, an MIT-licensed stealth Chromium wrapper. The upstream CloakBrowser project is available at https://github.com/CloakHQ/CloakBrowser.

## Safety

FareDrop does not submit passenger details or payment information. It records visible public fares, booking URLs, and screenshots so a human can verify possible mistake fares before taking action.
