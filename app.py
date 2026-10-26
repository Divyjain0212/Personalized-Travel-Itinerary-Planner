from __future__ import annotations

import streamlit as st
from dataclasses import replace

from travel_planner.models import TripPreferences
from travel_planner.pdf_export import build_itinerary_pdf
from travel_planner.services import (
    generate_itinerary,
    recommend_destinations,
    regenerate_day,
)
from travel_planner.storage import load_trip, load_trips, save_trip
from travel_planner.styles import inject_styles


st.set_page_config(
    page_title="Personalized Travel Itinerary Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()


def _init_state() -> None:
    defaults = {
        "recommendations": [],
        "itinerary": None,
        "preferences": None,
        "selected_trip_id": None,
        "notice": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _preference_form() -> TripPreferences | None:
    st.sidebar.markdown("## ✨ Trip brief")
    st.sidebar.caption("Use demo mode for a zero-key setup, or bring your own provider key.")
    provider = st.sidebar.selectbox("AI provider", ["Demo mode", "Google Gemini", "Groq"])
    api_key = st.sidebar.text_input(
        "API key",
        type="password",
        placeholder="Optional in demo mode",
        help="Keys are held only in this Streamlit session and are never saved with trips.",
    )
    if provider != "Demo mode" and not api_key:
        st.sidebar.info("Add a key to enable provider-backed generation. Demo mode remains available.")

    st.sidebar.divider()
    destination = st.sidebar.text_input("Destination", placeholder="e.g. Kyoto")
    vibe = st.sidebar.selectbox(
        "Open-ended travel vibe",
        ["Beach", "Mountains", "Cultural", "Urban"],
        disabled=bool(destination.strip()),
    )
    duration = st.sidebar.slider("Trip duration (days)", 1, 14, 5)
    dates = st.sidebar.date_input("Travel dates", value=[])
    budget = st.sidebar.selectbox("Budget level", ["Budget", "Moderate", "Luxury"])
    party = st.sidebar.selectbox("Travel party", ["Solo", "Couple", "Family", "Friends"])
    pace = st.sidebar.selectbox("Pace", ["Relaxed", "Moderate", "Fast-Paced"])
    interests = st.sidebar.multiselect(
        "Interests",
        ["Food", "Adventure", "History", "Nightlife"],
        default=["Food", "History"],
    )
    submitted = st.sidebar.button("Plan my trip", type="primary", use_container_width=True)
    if not submitted:
        return None

    travel_dates = []
    if isinstance(dates, tuple):
        travel_dates = list(dates)
    elif dates:
        travel_dates = [dates]
    return TripPreferences(
        destination=destination.strip(),
        vibe=vibe,
        duration_days=duration,
        travel_dates=travel_dates,
        budget=budget,
        party=party,
        pace=pace,
        interests=interests or ["Food"],
        provider=provider,
        api_key=api_key,
    )


def _show_recommendations(preferences: TripPreferences) -> None:
    st.subheader("Top matches for your travel mood")
    if preferences.destination:
        st.info(
            f"{preferences.destination} is selected. Explore alternatives below or open "
            "the Optimized itinerary tab to see your plan."
        )
        if st.button("Discover different destinations", key="discover-destinations"):
            st.session_state.preferences = replace(preferences, destination="")
            st.session_state.itinerary = None
            st.rerun()
        discovery_preferences = replace(preferences, destination="")
    else:
        discovery_preferences = preferences
    recommendations = recommend_destinations(discovery_preferences)
    st.session_state.recommendations = recommendations
    columns = st.columns(3)
    for column, recommendation in zip(columns, recommendations):
        with column:
            st.markdown(
                f"<div class='destination-card'><h3>{recommendation.city}</h3>"
                f"<p>{recommendation.country}</p><strong>{recommendation.match_score}% match</strong>"
                f"<p>{recommendation.reason}</p>"
                f"<div>{''.join(f'<span class=\"tag\">{tag}</span>' for tag in recommendation.tags)}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button(f"Plan {recommendation.city}", key=f"pick-{recommendation.city}"):
                selected_preferences = replace(preferences, destination=recommendation.city)
                st.session_state.preferences = selected_preferences
                try:
                    st.session_state.itinerary = generate_itinerary(selected_preferences)
                except (KeyError, ValueError, RuntimeError) as error:
                    st.error(f"Could not generate this itinerary: {error}")
                    return
                st.rerun()


def _render_itinerary(preferences: TripPreferences) -> None:
    itinerary = st.session_state.itinerary
    if not itinerary:
        st.info("Submit your trip brief to generate a day-by-day plan.")
        return
    st.subheader(f"{itinerary.title}")
    st.caption(
        f"{preferences.duration_days} days · {preferences.budget} · {preferences.party} · "
        f"Estimated total: {itinerary.total_cost_local:,.0f} {itinerary.currency} "
        f"(${itinerary.total_cost_usd:,.0f} / ₹{itinerary.total_cost_inr:,.0f})"
    )
    for day in itinerary.days:
        with st.expander(f"Day {day.day_number}: {day.area} — {day.daily_cost_local:,.0f} {itinerary.currency}", expanded=True):
            st.caption(day.route_summary)
            for slot in day.slots:
                st.markdown(
                    f"**{slot.time} · {slot.title}**  \n{slot.description}  \n"
                    f"<span class='cost'>≈ {slot.cost_local:,.0f} {itinerary.currency} "
                    f"(${slot.cost_usd:,.0f} / ₹{slot.cost_inr:,.0f})</span>",
                    unsafe_allow_html=True,
                )
            st.progress(min(day.cumulative_cost_local / max(itinerary.total_cost_local, 1), 1.0))
            st.caption(f"Running trip total: {day.cumulative_cost_local:,.0f} {itinerary.currency}")


def _swap_tab(preferences: TripPreferences) -> None:
    itinerary = st.session_state.itinerary
    if not itinerary:
        st.info("Generate an itinerary first to customize it.")
        return
    day_number = st.selectbox("Day to customize", [day.day_number for day in itinerary.days])
    day = itinerary.days[day_number - 1]
    slot_names = [slot.title for slot in day.slots]
    slot_index = st.selectbox(
        "Slot",
        range(len(slot_names)),
        format_func=lambda index: slot_names[index],
    )
    request = st.text_input(
        "What should change?",
        placeholder="e.g. Find vegetarian lunch spot or swap museum for outdoor market",
    )
    if st.button("Regenerate this day", type="primary"):
        if not request.strip():
            st.warning("Describe the swap so the planner can make a targeted change.")
        else:
            try:
                st.session_state.itinerary = regenerate_day(
                    itinerary, preferences, day_number, slot_index, request.strip()
                )
                st.success(f"Updated Day {day_number} without changing the rest of your plan.")
                st.rerun()
            except (IndexError, KeyError, ValueError) as error:
                st.error(f"Could not update that slot: {error}")


def _management_tab(preferences: TripPreferences) -> None:
    itinerary = st.session_state.itinerary
    if not itinerary:
        st.info("Generate an itinerary first to save or export it.")
        return
    left, right = st.columns([1, 1])
    with left:
        trip_name = st.text_input("Trip name", value=itinerary.title)
        if st.button("Save trip", type="primary"):
            try:
                trip_id = save_trip(trip_name, preferences, itinerary)
                st.session_state.selected_trip_id = trip_id
                st.success("Trip saved locally in the app workspace.")
            except (OSError, RuntimeError, ValueError) as error:
                st.error(f"Could not save this trip: {error}")
    with right:
        st.download_button(
            "Download offline PDF guide",
            data=build_itinerary_pdf(preferences, itinerary),
            file_name=f"{itinerary.slug}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    st.divider()
    st.subheader("Trip history")
    try:
        trips = load_trips()
    except RuntimeError as error:
        st.error(str(error))
        return
    if not trips:
        st.caption("Saved trips will appear here.")
    for trip in trips:
        with st.container(border=True):
            st.markdown(f"**{trip['name']}** · {trip['destination']} · {trip['saved_at']}")
            st.caption(f"{trip['duration_days']} days · {trip['budget']} · {trip['party']}")
            if st.button("Open trip", key=f"open-{trip['id']}"):
                try:
                    loaded_preferences, loaded_itinerary = load_trip(trip["id"])
                    st.session_state.preferences = loaded_preferences
                    st.session_state.itinerary = loaded_itinerary
                    st.success("Trip loaded.")
                    st.rerun()
                except (KeyError, TypeError, ValueError, RuntimeError) as error:
                    st.error(f"Could not open this trip: {error}")


def main() -> None:
    _init_state()
    st.markdown(
        "<div class='hero'><div class='eyebrow'>SKILL WALLET · CAPSTONE PROJECT 4</div>"
        "<h1>Personalized Travel<br><span>Itinerary Planner</span></h1>"
        "<p>Less transit. More stories. A thoughtful plan built around your way of travelling.</p></div>",
        unsafe_allow_html=True,
    )
    preferences = _preference_form()
    if preferences:
        st.session_state.preferences = preferences
        st.session_state.itinerary = (
            generate_itinerary(preferences) if preferences.destination else None
        )
        st.session_state.recommendations = recommend_destinations(preferences)
    preferences = st.session_state.preferences
    if not preferences:
        st.info("Start in the sidebar: choose your mood, pace, and interests.")
        return
    tabs = st.tabs(
        [
            "🌍 Smart destinations",
            "🗺️ Optimized itinerary",
            "🎨 Vibe & swaps",
            "💾 Manage & export",
        ]
    )
    with tabs[0]:
        _show_recommendations(preferences)
    with tabs[1]:
        _render_itinerary(preferences)
    with tabs[2]:
        _swap_tab(preferences)
    with tabs[3]:
        _management_tab(preferences)


if __name__ == "__main__":
    main()
