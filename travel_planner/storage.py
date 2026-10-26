from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from travel_planner.models import Itinerary, TripPreferences

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TRIPS_FILE = DATA_DIR / "trips.json"


def load_trips() -> list[dict]:
    try:
        if not TRIPS_FILE.exists():
            return []
        with TRIPS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Unable to read saved trips: {error}") from error


def save_trip(name: str, preferences: TripPreferences, itinerary: Itinerary) -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    trips = load_trips()
    trip_id = str(uuid4())
    trips.insert(
        0,
        {
            "id": trip_id,
            "name": name.strip() or itinerary.title,
            "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "destination": itinerary.destination,
            "duration_days": preferences.duration_days,
            "budget": preferences.budget,
            "party": preferences.party,
            "preferences": {
                key: value
                for key, value in preferences.__dict__.items()
                if key != "api_key"
            },
            "itinerary": itinerary.as_dict,
        },
    )
    try:
        with TRIPS_FILE.open("w", encoding="utf-8") as file:
            json.dump(trips[:25], file, indent=2, default=str)
    except OSError as error:
        raise RuntimeError(f"Unable to save trip: {error}") from error
    return trip_id


def load_trip(trip_id: str) -> tuple[TripPreferences, Itinerary]:
    trip = next((item for item in load_trips() if item.get("id") == trip_id), None)
    if not trip:
        raise ValueError("The selected saved trip could not be found.")
    raw_preferences = dict(trip["preferences"])
    raw_preferences["travel_dates"] = []
    # Backend-saved trips use the API names; the Streamlit prototype uses
    # ``party`` and does not have a group-size field.
    if "travel_party" in raw_preferences and "party" not in raw_preferences:
        raw_preferences["party"] = raw_preferences.pop("travel_party")
    raw_preferences.pop("group_size", None)
    preferences = TripPreferences(**raw_preferences)
    raw_itinerary = trip["itinerary"]
    from travel_planner.models import ActivitySlot, ItineraryDay

    days = [
        ItineraryDay(
            day_number=day["day_number"],
            area=day["area"],
            route_summary=day["route_summary"],
            slots=[ActivitySlot(**slot) for slot in day["slots"]],
        )
        for day in raw_itinerary["days"]
    ]
    itinerary = Itinerary(
        title=raw_itinerary["title"],
        destination=raw_itinerary["destination"],
        currency=raw_itinerary["currency"],
        slug=raw_itinerary.get(
            "slug",
            Itinerary.make_slug(
                f"{raw_itinerary['destination']}-{preferences.duration_days}-day-itinerary"
            ),
        ),
        days=days,
        usd_rate=raw_itinerary.get("usd_rate", 1.0),
    )
    itinerary.recalculate()
    return preferences, itinerary
