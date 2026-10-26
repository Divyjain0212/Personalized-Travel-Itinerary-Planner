from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TripPreferences(BaseModel):
    destination: str = ""
    vibe: Literal["Beach", "Mountains", "Cultural", "Urban"] = "Cultural"
    duration_days: int = Field(5, ge=1, le=30)
    travel_dates: list[date] = Field(default_factory=list)
    budget: Literal["Budget", "Moderate", "Luxury"] = "Moderate"
    travel_party: Literal["Solo", "Couple", "Family", "Friends"] = "Solo"
    pace: Literal["Relaxed", "Moderate", "Fast-Paced"] = "Moderate"
    interests: list[Literal["Food", "Adventure", "History", "Nightlife"]] = Field(default_factory=lambda: ["Food"])
    group_size: int = Field(1, ge=1, le=50)


class AIConfig(BaseModel):
    provider: Literal["demo", "gemini", "groq"] = "demo"
    api_key: str | None = Field(default=None, max_length=500)


class GenerateRequest(BaseModel):
    preferences: TripPreferences
    ai: AIConfig = Field(default_factory=AIConfig)


class DestinationRecommendation(BaseModel):
    city: str
    country: str
    match_score: int
    reason: str
    tags: list[str]


class ActivitySlot(BaseModel):
    time: str
    title: str
    description: str
    cost_local: float
    cost_usd: float
    cost_inr: float
    category: str


class ItineraryDay(BaseModel):
    day_number: int
    area: str
    route_summary: str
    slots: list[ActivitySlot]
    daily_cost_local: float = 0
    cumulative_cost_local: float = 0


class Itinerary(BaseModel):
    title: str
    destination: str
    currency: str
    usd_rate: float
    days: list[ItineraryDay]
    total_cost_local: float = 0
    total_cost_usd: float = 0
    total_cost_inr: float = 0


class PlanResponse(BaseModel):
    preferences: TripPreferences
    recommendations: list[DestinationRecommendation]
    itinerary: Itinerary | None = None


class SwapRequest(BaseModel):
    preferences: TripPreferences
    ai: AIConfig = Field(default_factory=AIConfig)
    day_number: int = Field(ge=1)
    slot_index: int = Field(ge=0, le=3)
    request: str = Field(min_length=3, max_length=500)
    itinerary: Itinerary


class SaveTripRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    preferences: TripPreferences
    itinerary: Itinerary


class SavedTrip(BaseModel):
    id: str
    name: str
    destination: str
    duration_days: int
    budget: str
    saved_at: str
    preferences: TripPreferences
    itinerary: Itinerary
