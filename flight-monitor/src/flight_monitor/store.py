from __future__ import annotations

import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from flight_monitor.models import FareResult


class FareStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS fares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    depart_date TEXT NOT NULL,
                    return_date TEXT,
                    price TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    airline TEXT,
                    flight_no TEXT,
                    stops INTEGER,
                    duration_minutes INTEGER,
                    booking_url TEXT NOT NULL,
                    screenshot_path TEXT,
                    captured_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_fares_route_date
                ON fares(origin, destination, depart_date, captured_at)
                """
            )

    def insert_fare(self, fare: FareResult) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO fares (
                    provider, origin, destination, depart_date, return_date, price,
                    currency, airline, flight_no, stops, duration_minutes,
                    booking_url, screenshot_path, captured_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fare.provider,
                    fare.origin,
                    fare.destination,
                    fare.depart_date.isoformat(),
                    fare.return_date.isoformat() if fare.return_date else None,
                    str(fare.price),
                    fare.currency,
                    fare.airline,
                    fare.flight_no,
                    fare.stops,
                    fare.duration_minutes,
                    fare.booking_url,
                    fare.screenshot_path,
                    fare.captured_at.isoformat(),
                ),
            )

    def recent_fares(self, origin: str, destination: str, depart_date: date, limit: int) -> list[FareResult]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM fares
                WHERE origin = ? AND destination = ? AND depart_date = ?
                ORDER BY captured_at DESC
                LIMIT ?
                """,
                (origin, destination, depart_date.isoformat(), limit),
            ).fetchall()
        return [self._row_to_fare(row) for row in rows]

    def all_fares(self) -> list[FareResult]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM fares ORDER BY captured_at DESC").fetchall()
        return [self._row_to_fare(row) for row in rows]

    def _row_to_fare(self, row: sqlite3.Row) -> FareResult:
        return FareResult(
            provider=row["provider"],
            origin=row["origin"],
            destination=row["destination"],
            depart_date=date.fromisoformat(row["depart_date"]),
            return_date=date.fromisoformat(row["return_date"]) if row["return_date"] else None,
            price=Decimal(row["price"]),
            currency=row["currency"],
            airline=row["airline"],
            flight_no=row["flight_no"],
            stops=row["stops"],
            duration_minutes=row["duration_minutes"],
            booking_url=row["booking_url"],
            screenshot_path=row["screenshot_path"],
            captured_at=datetime.fromisoformat(row["captured_at"]),
        )
