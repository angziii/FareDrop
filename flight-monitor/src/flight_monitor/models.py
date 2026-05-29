from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


TripType = Literal["one_way", "round_trip"]
ProviderName = Literal["trip", "hopegoo", "qunar"]


class Travelers(BaseModel):
    adults: int = Field(default=1, ge=1, le=9)


class RouteSpec(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destinations: list[str] = Field(min_length=1)


class DateWindow(BaseModel):
    start: date
    end: date


class MonitorConfig(BaseModel):
    currency: str = "CNY"
    trip_type: TripType = "one_way"
    travelers: Travelers = Field(default_factory=Travelers)
    routes: list[RouteSpec] = Field(min_length=1)
    date_windows: list[DateWindow] = Field(min_length=1)
    providers: list[ProviderName] = Field(default_factory=lambda: ["trip", "hopegoo"])


class SearchRequest(BaseModel):
    origin: str
    destination: str
    depart_date: date
    return_date: date | None = None
    currency: str = "CNY"
    adults: int = 1
    trip_type: TripType = "one_way"


class FareResult(BaseModel):
    provider: str
    origin: str
    destination: str
    depart_date: date
    return_date: date | None = None
    price: Decimal
    currency: str
    airline: str | None = None
    flight_no: str | None = None
    stops: int | None = None
    duration_minutes: int | None = None
    booking_url: str
    screenshot_path: str | None = None
    captured_at: datetime
