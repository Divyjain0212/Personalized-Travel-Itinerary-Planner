from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from travel_planner.models import Itinerary, TripPreferences


def build_itinerary_pdf(preferences: TripPreferences, itinerary: Itinerary) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=itinerary.title,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Kicker", parent=styles["Normal"], textColor=colors.HexColor("#f97316"), fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="TravelTitle", parent=styles["Title"], textColor=colors.HexColor("#0e7490"), fontSize=24, leading=28))
    styles.add(ParagraphStyle(name="DayHeading", parent=styles["Heading2"], textColor=colors.HexColor("#155e75"), spaceBefore=12))
    story = [
        Paragraph("PERSONALIZED TRAVEL GUIDE", styles["Kicker"]),
        Paragraph(itinerary.title, styles["TravelTitle"]),
        Paragraph(
            f"{preferences.party} · {preferences.pace} pace · {preferences.budget} budget · "
            f"Estimated {itinerary.total_cost_local:,.0f} {itinerary.currency} "
            f"(${itinerary.total_cost_usd:,.0f} / ₹{itinerary.total_cost_inr:,.0f})",
            styles["Normal"],
        ),
        Spacer(1, 8 * mm),
    ]
    for day in itinerary.days:
        story.append(Paragraph(f"Day {day.day_number} · {day.area}", styles["DayHeading"]))
        story.append(Paragraph(day.route_summary, styles["Normal"]))
        rows = [["Time", "Plan", "Estimated cost"]]
        for slot in day.slots:
            rows.append(
                [
                    slot.time,
                    Paragraph(f"<b>{slot.title}</b><br/>{slot.description}", styles["Normal"]),
                    f"{slot.cost_local:,.0f} {itinerary.currency}",
                ]
            )
        table = Table(rows, colWidths=[22 * mm, 112 * mm, 35 * mm], repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0e7490")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.extend([table, Spacer(1, 5 * mm)])
    story.extend(
        [
            PageBreak(),
            Paragraph("Emergency checklist", styles["DayHeading"]),
            Paragraph(
                "[ ] Save your accommodation address offline<br/>"
                "[ ] Add local emergency services to your phone<br/>"
                "[ ] Carry a copy of passport and travel insurance<br/>"
                "[ ] Share your itinerary and check-in plan with a trusted contact<br/>"
                "[ ] Keep a backup payment method separate from your wallet",
                styles["Normal"],
            ),
            Spacer(1, 8 * mm),
            Paragraph("This guide is a planning aid. Confirm opening hours, transport, weather, and local advisories before departure.", styles["Italic"]),
        ]
    )
    document.build(story)
    return output.getvalue()
