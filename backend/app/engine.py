from copy import deepcopy

from .schemas import (
    ActivitySlot,
    DestinationRecommendation,
    Itinerary,
    ItineraryDay,
    TripPreferences,
)


DESTINATIONS = [
    ("Lisbon", "Portugal", "Sunny, walkable neighbourhoods with excellent value and a strong food scene.", ["Food", "Urban", "Value"], 94),
    ("Kyoto", "Japan", "A calm cultural rhythm with remarkable history, gardens, and seasonal beauty.", ["History", "Cultural", "Slow travel"], 92),
    ("Bali", "Indonesia", "A flexible island base for wellness, beaches, adventure, and local meals.", ["Beach", "Adventure", "Relaxed"], 91),
    ("Barcelona", "Spain", "Architecture, tapas, beaches, and late-night energy in one walkable city.", ["Food", "Urban", "Nightlife"], 89),
    ("Queenstown", "New Zealand", "Mountain scenery and outdoor thrills with a clear travel flow.", ["Mountains", "Adventure", "Scenic"], 87),
    ("Jaipur", "India", "Forts, craft markets, and generous cuisine for culture-first travellers.", ["History", "Food", "Value"], 86),
]
CITY_DATA = {
    "lisbon": ("EUR", 1.08, ["Baixa & Alfama", "Belém", "Príncipe Real", "Parque das Nações"]),
    "kyoto": ("JPY", 0.0067, ["Higashiyama", "Arashiyama", "Gion", "Fushimi"]),
    "bali": ("IDR", 0.000061, ["Ubud", "Canggu", "Uluwatu", "Sanur"]),
    "barcelona": ("EUR", 1.08, ["Gothic Quarter", "Eixample", "Montjuïc", "Barceloneta"]),
    "queenstown": ("NZD", 0.60, ["Queenstown Gardens", "Arrowtown", "Lake Wakatipu", "Ben Lomond"]),
    "jaipur": ("INR", 0.012, ["Pink City", "Amer", "Bapu Bazaar", "C-Scheme"]),
}
BASE = {
    "Sightseeing": ("09:00", "Morning Sightseeing", "Explore a signature landmark cluster with a local guide.", 35),
    "Lunch": ("12:30", "Lunch Recommendation", "A well-reviewed neighbourhood table with a local speciality.", 18),
    "Leisure": ("15:00", "Afternoon Leisure", "Keep the afternoon flexible for a scenic walk, market, or café stop.", 20),
    "Evening": ("19:00", "Evening Dining & Entertainment", "A relaxed dinner followed by a memorable local experience.", 42),
}


def recommendations(preferences: TripPreferences) -> list[DestinationRecommendation]:
    if preferences.destination:
        return [DestinationRecommendation(city=preferences.destination, country="Selected destination", match_score=100, reason="Your route will be clustered by neighbourhood to reduce transit fatigue.", tags=preferences.interests[:3] or ["Personalised"])]
    scored = []
    for city, country, reason, tags, base_score in DESTINATIONS:
        score = base_score + (4 if preferences.vibe in tags else 0)
        score += min(6, len(set(preferences.interests) & set(tags)) * 2)
        score += 3 if preferences.budget == "Budget" and "Value" in tags else 0
        scored.append((min(score, 100), city, country, reason, tags))
    return [DestinationRecommendation(match_score=score, city=city, country=country, reason=reason, tags=tags) for score, city, country, reason, tags in sorted(scored, reverse=True)[:3]]


def _slot(kind: str, preferences: TripPreferences, request: str = "") -> ActivitySlot:
    time, title, description, base_cost = BASE[kind]
    lower_request = request.lower()
    if kind == "Lunch" and "vegetarian" in lower_request:
        title, description = "Vegetarian Lunch Recommendation", "A highly rated vegetarian-friendly restaurant with regional flavours."
    if kind == "Sightseeing" and ("market" in lower_request or "outdoor" in lower_request):
        title, description = "Outdoor Market Stroll", "An open-air market for crafts, snacks, and neighbourhood life."
    currency, usd_rate, _ = CITY_DATA.get(preferences.destination.lower(), ("USD", 1.0, []))
    cost = base_cost * {"Budget": 0.7, "Moderate": 1.0, "Luxury": 1.8}[preferences.budget] / usd_rate
    return ActivitySlot(time=time, title=title, description=description, cost_local=cost, cost_usd=cost * usd_rate, cost_inr=cost * usd_rate * 84, category=kind)


def generate(preferences: TripPreferences) -> Itinerary:
    destination = preferences.destination or recommendations(preferences)[0].city
    currency, usd_rate, areas = CITY_DATA.get(destination.lower(), ("USD", 1.0, ["City centre", "Old town", "Waterfront", "Arts district"]))
    days = [ItineraryDay(day_number=index + 1, area=areas[index % len(areas)], route_summary=f"Stay within {areas[index % len(areas)]}; nearby stops are grouped to avoid backtracking.", slots=[_slot(kind, preferences) for kind in BASE]) for index in range(preferences.duration_days)]
    itinerary = Itinerary(title=f"{destination}: your {preferences.duration_days}-day story", destination=destination, currency=currency, usd_rate=usd_rate, days=days)
    return recalculate(itinerary)


def recalculate(itinerary: Itinerary) -> Itinerary:
    running = 0.0
    for day in itinerary.days:
        day.daily_cost_local = sum(slot.cost_local for slot in day.slots)
        running += day.daily_cost_local
        day.cumulative_cost_local = running
    itinerary.total_cost_local = running
    itinerary.total_cost_usd = running * itinerary.usd_rate
    itinerary.total_cost_inr = itinerary.total_cost_usd * 84
    return itinerary


def swap_day(itinerary: Itinerary, preferences: TripPreferences, day_number: int, slot_index: int, request: str) -> Itinerary:
    updated = deepcopy(itinerary)
    slot = updated.days[day_number - 1].slots[slot_index]
    updated.days[day_number - 1].slots[slot_index] = _slot(slot.category, preferences, request)
    return recalculate(updated)
