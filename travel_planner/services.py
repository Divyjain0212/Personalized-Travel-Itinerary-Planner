from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from travel_planner.models import (
    ActivitySlot,
    DestinationRecommendation,
    Itinerary,
    ItineraryDay,
    TripPreferences,
)

DESTINATIONS = [
    DestinationRecommendation("Lisbon", "Portugal", 94, "Sunny, walkable neighbourhoods with excellent value and a strong food scene.", ["Food", "Urban", "Value"], ("Spring", "Summer", "Autumn")),
    DestinationRecommendation("Kyoto", "Japan", 92, "A calm cultural rhythm with remarkable history, gardens, and seasonal beauty.", ["History", "Cultural", "Slow travel"], ("Spring", "Autumn")),
    DestinationRecommendation("Bali", "Indonesia", 91, "A flexible island base for wellness, beaches, adventure, and memorable local meals.", ["Beach", "Adventure", "Relaxed"], ("Spring", "Summer", "Autumn")),
    DestinationRecommendation("Barcelona", "Spain", 89, "A lively city break pairing architecture, tapas, beaches, and late-night energy.", ["Food", "Urban", "Nightlife"], ("Spring", "Summer", "Autumn")),
    DestinationRecommendation("Queenstown", "New Zealand", 87, "Mountain scenery and outdoor thrills with a clear, easy-to-follow travel flow.", ["Mountains", "Adventure", "Scenic"], ("Winter", "Spring", "Summer")),
    DestinationRecommendation("Jaipur", "India", 86, "Colourful forts, craft markets, and generous cuisine for culture-first travellers.", ["History", "Food", "Value"], ("Winter", "Spring", "Autumn")),
]

CITY_DATA = {
    "lisbon": ("EUR", 1.08, ["Baixa & Alfama", "Belém", "Príncipe Real", "Parque das Nações"]),
    "kyoto": ("JPY", 0.0067, ["Higashiyama", "Arashiyama", "Gion", "Fushimi"]),
    "bali": ("IDR", 0.000061, ["Ubud", "Canggu", "Uluwatu", "Sanur"]),
    "barcelona": ("EUR", 1.08, ["Gothic Quarter", "Eixample", "Montjuïc", "Barceloneta"]),
    "queenstown": ("NZD", 0.60, ["Queenstown Gardens", "Arrowtown", "Lake Wakatipu", "Ben Lomond"]),
    "jaipur": ("INR", 0.012, ["Pink City", "Amer", "Bapu Bazaar", "C-Scheme"]),
}

BASE_ACTIVITIES = {
    "Sightseeing": ("Morning Sightseeing", "Explore a signature landmark cluster with a local guide.", 35),
    "Lunch": ("Lunch Recommendation", "A well-reviewed neighbourhood table with a local speciality.", 18),
    "Leisure": ("Afternoon Leisure", "Keep the afternoon flexible for a scenic walk, market, or café stop.", 20),
    "Evening": ("Evening Dining & Entertainment", "A relaxed dinner followed by a memorable local experience.", 42),
}

CITY_PLANS = {
    "lisbon": {
        "Baixa & Alfama": [
            ("Morning Sightseeing", "Ride Tram 28 through Alfama, then walk to São Jorge Castle for hilltop views."),
            ("Lunch Recommendation", "Try a family-run tasca for bacalhau, caldo verde, and a small glass of vinho verde."),
            ("Afternoon Leisure", "Wander the tiled lanes, Miradouro de Santa Luzia, and the Sé cathedral terraces."),
            ("Evening Dining & Entertainment", "Enjoy petiscos in Bairro Alto, followed by an intimate Fado performance."),
        ],
        "Belém": [
            ("Morning Sightseeing", "Visit Jerónimos Monastery and the Monument to the Discoveries along the riverfront."),
            ("Lunch Recommendation", "Stop for a seafood lunch near the waterfront, then share a warm pastel de nata."),
            ("Afternoon Leisure", "Walk the gardens from Belém Tower to MAAT with a sunset river breeze."),
            ("Evening Dining & Entertainment", "Return to the centre for a relaxed Portuguese dinner in Chiado."),
        ],
    },
    "kyoto": {
        "Higashiyama": [
            ("Morning Sightseeing", "Start early at Kiyomizu-dera, then follow the preserved Ninenzaka and Sannenzaka lanes."),
            ("Lunch Recommendation", "Choose a seasonal tofu or soba set in a quiet Higashiyama restaurant."),
            ("Afternoon Leisure", "Unwind in Maruyama Park and explore the craft shops around Gion."),
            ("Evening Dining & Entertainment", "Reserve a small Kyoto kaiseki or izakaya table near Pontocho."),
        ],
        "Arashiyama": [
            ("Morning Sightseeing", "Walk the bamboo grove early and continue to Tenryu-ji temple gardens."),
            ("Lunch Recommendation", "Enjoy yudofu or a vegetarian-friendly set meal near the river."),
            ("Afternoon Leisure", "Cross Togetsukyo Bridge and take a slow riverside walk through Saga."),
            ("Evening Dining & Entertainment", "Return to Gion for tea, lantern-lit lanes, and a compact dinner."),
        ],
    },
    "bali": {
        "Ubud": [
            ("Morning Sightseeing", "Visit the Sacred Monkey Forest and nearby Ubud palace before the crowds build."),
            ("Lunch Recommendation", "Choose a local warung with rice bowls, fresh vegetables, and tropical juice."),
            ("Afternoon Leisure", "Walk the Campuhan Ridge trail and leave time for a restorative spa treatment."),
            ("Evening Dining & Entertainment", "Book a candlelit farm-to-table dinner with a traditional dance performance."),
        ],
        "Canggu": [
            ("Morning Sightseeing", "Take a relaxed coastal cycle through rice fields toward the black-sand beach."),
            ("Lunch Recommendation", "Find a healthy café bowl or Indonesian seafood lunch near the beach."),
            ("Afternoon Leisure", "Spend the afternoon surfing, swimming, or reading at a beach club."),
            ("Evening Dining & Entertainment", "Watch sunset at Echo Beach, then explore Canggu’s live-music scene."),
        ],
    },
    "barcelona": {
        "Gothic Quarter": [
            ("Morning Sightseeing", "Walk the Roman walls, Barcelona Cathedral, and the tucked-away Plaça de Sant Felip Neri."),
            ("Lunch Recommendation", "Share a Catalan lunch of tapas, pa amb tomàquet, and seasonal dishes."),
            ("Afternoon Leisure", "Browse the Boqueria market and wander through El Born’s independent shops."),
            ("Evening Dining & Entertainment", "Book a late dinner in El Born, then catch live jazz or a flamenco set."),
        ],
        "Eixample": [
            ("Morning Sightseeing", "Follow Gaudí’s modernist route from Casa Batlló to La Pedrera."),
            ("Lunch Recommendation", "Try a neighbourhood menu del día with a relaxed Catalan dessert."),
            ("Afternoon Leisure", "Take coffee and gallery breaks along Rambla de Catalunya."),
            ("Evening Dining & Entertainment", "Dine around Sant Antoni and finish with a rooftop cocktail."),
        ],
    },
    "queenstown": {
        "Queenstown Gardens": [
            ("Morning Sightseeing", "Walk Queenstown Gardens and take the Skyline gondola for lake and mountain views."),
            ("Lunch Recommendation", "Choose a hearty local lunch with a view of Lake Wakatipu."),
            ("Afternoon Leisure", "Cruise the lake or take an easy lakeside cycle at your chosen pace."),
            ("Evening Dining & Entertainment", "Enjoy a warm South Island dinner and a stargazing walk."),
        ],
        "Arrowtown": [
            ("Morning Sightseeing", "Explore Arrowtown’s gold-rush cottages and the riverside Chinese settlement."),
            ("Lunch Recommendation", "Settle into a country café for a seasonal pie or locally sourced plate."),
            ("Afternoon Leisure", "Follow the Arrow River trail with a scenic stop for photos."),
            ("Evening Dining & Entertainment", "Return to Queenstown for a relaxed dinner overlooking the lake."),
        ],
    },
    "jaipur": {
        "Pink City": [
            ("Morning Sightseeing", "Visit Amber Fort and the City Palace before the afternoon heat."),
            ("Lunch Recommendation", "Enjoy a thali with regional Rajasthani specialities and cooling lassi."),
            ("Afternoon Leisure", "Browse block prints and crafts around Johari Bazaar with a local guide."),
            ("Evening Dining & Entertainment", "Dine on a rooftop with Pink City views and a folk music set."),
        ],
        "Amer": [
            ("Morning Sightseeing", "Explore Amer’s fort courtyards, Sheesh Mahal, and the old stepwell nearby."),
            ("Lunch Recommendation", "Choose a family kitchen for dal baati churma and seasonal vegetables."),
            ("Afternoon Leisure", "Slow down at Jal Mahal viewpoints and a quiet artisan workshop."),
            ("Evening Dining & Entertainment", "Return to the city for a haveli dinner and cultural performance."),
        ],
    },
}


def recommend_destinations(preferences: TripPreferences) -> list[DestinationRecommendation]:
    if preferences.destination:
        return [
            DestinationRecommendation(
                preferences.destination,
                "Your chosen destination",
                100,
                "Your plan will be clustered into neighbourhoods to keep travel time low.",
                preferences.interests[:3] or ["Personalised"],
            )
        ]
    month = preferences.travel_dates[0].month if preferences.travel_dates else None
    season = (
        "Winter" if month in (12, 1, 2) else
        "Spring" if month in (3, 4, 5) else
        "Summer" if month in (6, 7, 8) else
        "Autumn" if month in (9, 10, 11) else None
    )
    scored = []
    for item in DESTINATIONS:
        score = item.match_score
        if preferences.vibe in item.tags:
            score += 4
        score += min(len(set(preferences.interests) & set(item.tags)) * 2, 6)
        if preferences.budget == "Budget" and "Value" in item.tags:
            score += 3
        if season and season in item.best_seasons:
            score += 4
        scored.append((min(score, 100), item))
    return [
        DestinationRecommendation(item.city, item.country, score, item.reason, item.tags, item.best_seasons)
        for score, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:3]
    ]


def _slot(
    kind: str,
    preferences: TripPreferences,
    request: str = "",
    custom_content: tuple[str, str] | None = None,
) -> ActivitySlot:
    title, description, base_cost = BASE_ACTIVITIES[kind]
    if custom_content:
        title, description = custom_content
    if request and kind == "Lunch" and "vegetarian" in request.lower():
        title = "Vegetarian Lunch Recommendation"
        description = "A highly rated vegetarian-friendly restaurant with regional flavours and easy ordering."
    elif request and kind == "Sightseeing" and any(word in request.lower() for word in ("market", "outdoor")):
        title = "Outdoor Market Stroll"
        description = "Swap the museum for an open-air market: browse crafts, snacks, and neighbourhood life."
    multiplier = {"Budget": 0.7, "Moderate": 1.0, "Luxury": 1.8}[preferences.budget]
    destination = preferences.destination.lower()
    usd_rate = CITY_DATA.get(destination, ("USD", 1.0, []))[1]
    cost = (base_cost / usd_rate) * multiplier
    return ActivitySlot(
        time={"Sightseeing": "09:00", "Lunch": "12:30", "Leisure": "15:00", "Evening": "19:00"}[kind],
        title=title,
        description=description,
        cost_local=cost,
        cost_usd=cost * usd_rate,
        cost_inr=cost * usd_rate * 84,
        category=kind,
    )


def generate_itinerary(preferences: TripPreferences) -> Itinerary:
    destination = preferences.destination or recommend_destinations(preferences)[0].city
    currency, usd_rate, areas = CITY_DATA.get(destination.lower(), ("USD", 1.0, ["City centre", "Old town", "Waterfront", "Arts district"]))
    planning_preferences = replace(preferences, destination=destination)
    city_plan = CITY_PLANS.get(destination.lower(), {})
    days = []
    for index in range(preferences.duration_days):
        area = areas[index % len(areas)]
        plan = city_plan.get(area)
        slots = [
            _slot(
                kind,
                planning_preferences,
                custom_content=next(
                    (content for content in plan or [] if content[0] == BASE_ACTIVITIES[kind][0]),
                    None,
                ),
            )
            for kind in ("Sightseeing", "Lunch", "Leisure", "Evening")
        ]
        days.append(
            ItineraryDay(
                index + 1,
                area,
                f"Stay within {area}; nearby stops are grouped to avoid backtracking.",
                slots,
            )
        )
    itinerary = Itinerary(
        title=f"{destination}: your {preferences.duration_days}-day story",
        destination=destination,
        currency=currency,
        slug=Itinerary.make_slug(f"{destination}-{preferences.duration_days}-day-itinerary"),
        days=days,
        usd_rate=usd_rate,
    )
    itinerary.recalculate()
    return itinerary


def regenerate_day(
    itinerary: Itinerary,
    preferences: TripPreferences,
    day_number: int,
    slot_index: int,
    request: str,
) -> Itinerary:
    updated = deepcopy(itinerary)
    day = updated.days[day_number - 1]
    slot = day.slots[slot_index]
    day.slots[slot_index] = _slot(slot.category, preferences, request)
    updated.recalculate()
    return updated
