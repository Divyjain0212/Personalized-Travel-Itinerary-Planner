import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import get_settings
from .schemas import SavedTrip


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "trips.json"


def _supabase_client():
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        return None
    from supabase import create_client

    return create_client(settings.supabase_url, settings.supabase_service_key)


def list_trips() -> list[SavedTrip]:
    client = _supabase_client()
    if client:
        response = client.table("trips").select("*").order("saved_at", desc=True).execute()
        return [SavedTrip.model_validate(item) for item in response.data]
    if not DATA_FILE.exists():
        return []
    try:
        return [SavedTrip.model_validate(item) for item in json.loads(DATA_FILE.read_text(encoding="utf-8"))]
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(f"Unable to read trip history: {error}") from error


def save_trip(name: str, preferences, itinerary) -> SavedTrip:
    trip = SavedTrip(
        id=str(uuid4()),
        name=name.strip() or itinerary.title,
        destination=itinerary.destination,
        duration_days=preferences.duration_days,
        budget=preferences.budget,
        saved_at=datetime.now(timezone.utc).isoformat(),
        preferences=preferences,
        itinerary=itinerary,
    )
    client = _supabase_client()
    if client:
        client.table("trips").insert(trip.model_dump(mode="json")).execute()
        return trip
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        trips = [trip, *list_trips()]
        DATA_FILE.write_text(json.dumps([item.model_dump(mode="json") for item in trips[:50]], indent=2), encoding="utf-8")
        return trip
    except OSError as error:
        raise RuntimeError(f"Unable to save trip: {error}") from error
