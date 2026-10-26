from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re


@dataclass
class TripPreferences:
    destination: str
    vibe: str
    duration_days: int
    travel_dates: list[date]
    budget: str
    party: str
    pace: str
    interests: list[str]
    provider: str = "Demo mode"
    api_key: str = ""


@dataclass(frozen=True)
class DestinationRecommendation:
    city: str
    country: str
    match_score: int
    reason: str
    tags: list[str]
    best_seasons: tuple[str, ...] = ()


@dataclass
class ActivitySlot:
    time: str
    title: str
    description: str
    cost_local: float
    cost_usd: float
    cost_inr: float
    category: str


@dataclass
class ItineraryDay:
    day_number: int
    area: str
    route_summary: str
    slots: list[ActivitySlot]
    daily_cost_local: float = 0
    cumulative_cost_local: float = 0


@dataclass
class Itinerary:
    title: str
    destination: str
    currency: str
    slug: str
    days: list[ItineraryDay]
    usd_rate: float = 1.0
    total_cost_local: float = 0
    total_cost_usd: float = 0
    total_cost_inr: float = 0

    def recalculate(self) -> None:
        running = 0.0
        for day in self.days:
            day.daily_cost_local = sum(slot.cost_local for slot in day.slots)
            running += day.daily_cost_local
            day.cumulative_cost_local = running
        self.total_cost_local = running
        self.total_cost_usd = running * self.usd_rate
        self.total_cost_inr = self.total_cost_usd * 84

    @property
    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "destination": self.destination,
            "currency": self.currency,
            "slug": self.slug,
            "usd_rate": self.usd_rate,
            "days": [
                {
                    "day_number": day.day_number,
                    "area": day.area,
                    "route_summary": day.route_summary,
                    "slots": [slot.__dict__ for slot in day.slots],
                }
                for day in self.days
            ],
        }

    @staticmethod
    def make_slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "trip"
