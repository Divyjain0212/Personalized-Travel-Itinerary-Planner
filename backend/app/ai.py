from .config import get_settings
from .schemas import Itinerary, TripPreferences


async def generate_with_provider(preferences: TripPreferences) -> Itinerary | None:
    """Provider seam for Gemini/Groq prompt execution; demo mode uses the deterministic engine."""
    settings = get_settings()
    if settings.gemini_api_key or settings.groq_api_key:
        # Keep provider calls behind this boundary so prompts, retries, and structured
        # response validation can evolve without changing the API contract.
        return None
    return None
