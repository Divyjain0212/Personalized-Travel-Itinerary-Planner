from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .engine import generate, recommendations, swap_day
from .repository import list_trips, save_trip
from .schemas import GenerateRequest, PlanResponse, SaveTripRequest, SwapRequest, TripPreferences

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.post("/api/recommendations", response_model=list)
def get_recommendations(preferences: TripPreferences):
    return recommendations(preferences)


@app.post("/api/itineraries/generate", response_model=PlanResponse)
def generate_itinerary(request: GenerateRequest):
    if request.ai.provider != "demo" and not request.ai.api_key:
        raise HTTPException(status_code=400, detail="An API key is required for the selected provider.")
    itinerary = generate(request.preferences) if request.preferences.destination else None
    return PlanResponse(
        preferences=request.preferences,
        recommendations=recommendations(request.preferences),
        itinerary=itinerary,
    )


@app.post("/api/itineraries/swap", response_model=PlanResponse)
def regenerate_day(request: SwapRequest):
    if request.ai.provider != "demo" and not request.ai.api_key:
        raise HTTPException(status_code=400, detail="An API key is required for the selected provider.")
    try:
        itinerary = swap_day(
            request.itinerary,
            request.preferences,
            request.day_number,
            request.slot_index,
            request.request,
        )
    except (IndexError, KeyError) as error:
        raise HTTPException(status_code=400, detail="Invalid day or activity slot.") from error
    return PlanResponse(preferences=request.preferences, recommendations=recommendations(request.preferences), itinerary=itinerary)


@app.get("/api/trips")
def get_trips():
    try:
        return list_trips()
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/api/trips")
def create_trip(request: SaveTripRequest):
    try:
        return save_trip(request.name, request.preferences, request.itinerary)
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
