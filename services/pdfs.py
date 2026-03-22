from io import BytesIO
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def _draw_header(c: canvas.Canvas, title: str, logo_path: str = "assets/logo.png"):
    width, height = A4
    y = height - 1.5 * cm

    # Logo (optional)
    p = Path(logo_path)
    if p.exists():
        try:
            img = ImageReader(str(p))
            c.drawImage(img, 1.2 * cm, y - 1.2 * cm, width=3.0 * cm, height=3.0 * cm, mask='auto')
        except Exception:
            pass

    c.setFont("Helvetica-Bold", 18)
    c.drawString(5.0 * cm, y, title)

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 1.2 * cm, y, datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Divider
    c.setLineWidth(1)
    c.line(1.2 * cm, y - 0.6 * cm, width - 1.2 * cm, y - 0.6 * cm)

    return y - 1.2 * cm

def _new_pdf() -> tuple[BytesIO, canvas.Canvas]:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    return buf, c

def _finish_pdf(buf: BytesIO, c: canvas.Canvas) -> bytes:
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def make_program_pdf(trip: dict, traveler_name: str, itinerary_rows: list[dict]) -> bytes:
    buf, c = _new_pdf()
    y = _draw_header(c, "MySafar – Trip Program")

    width, height = A4
    left = 1.2 * cm
    right = width - 1.2 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, f"Traveler: {traveler_name}")
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    c.drawString(left, y, f"Trip: {trip['origin_city']} → {trip['destination_city']} ({trip['destination_country']})")
    y -= 0.5 * cm
    c.drawString(left, y, f"Dates: {trip['start_date']} → {trip['end_date']} | Type: {trip['travel_type']}")
    y -= 0.9 * cm

    # Group by day
    by_day = defaultdict(list)
    for r in itinerary_rows:
        by_day[r["day_date"]].append(r)

    for day, rows in sorted(by_day.items()):
        if y < 3 * cm:
            c.showPage()
            y = _draw_header(c, "MySafar – Trip Program")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(left, y, str(day))
        y -= 0.5 * cm

        c.setFont("Helvetica", 10)
        for r in rows:
            line = f"{r['start_time'][:5]}–{r['end_time'][:5]}  |  {r['poi_name']}  |  {r.get('poi_category','')}"
            c.drawString(left + 0.3 * cm, y, line)
            y -= 0.4 * cm
            if r.get("address"):
                c.setFont("Helvetica-Oblique", 9)
                c.drawString(left + 0.9 * cm, y, f"Address: {r['address']}")
                y -= 0.35 * cm
                c.setFont("Helvetica", 10)
            if y < 2.5 * cm:
                c.showPage()
                y = _draw_header(c, "MySafar – Trip Program")

        y -= 0.3 * cm

    return _finish_pdf(buf, c)

def make_safety_pdf(trip: dict, traveler_name: str, travel_type: str) -> bytes:
    buf, c = _new_pdf()
    y = _draw_header(c, "MySafar – Safety Tips & Checklist")

    width, height = A4
    left = 1.2 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, f"Traveler: {traveler_name}")
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    c.drawString(left, y, f"Destination: {trip['destination_city']} ({trip['destination_country']}) | Travel type: {travel_type}")
    y -= 0.9 * cm

    checklist = [
        "Passport (valid, sufficient validity remaining)",
        "Visa (if required) + visa number (if applicable)",
        "Flight booking confirmation / e-ticket",
        "Hotel/accommodation confirmations (if applicable)",
        "Travel insurance documents",
        "Payment method(s): card + some cash",
        "Emergency contact list",
        "Local transport plan (SIM/eSIM, maps offline)",
        "Copies of key documents (digital + paper)",
    ]

    tips = [
        "Keep passport and valuables secured; avoid carrying everything in one place.",
        "Use official transport options and verify pickup details when booking rides.",
        "Keep digital backups of documents (encrypted if possible).",
        "Share itinerary with a trusted contact.",
        "Check local rules (customs, medications, photography restrictions).",
        "For business trips: plan visits after work and keep buffers between appointments.",
        "Check attraction opening hours the day before (they can change).",
    ]

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Checklist")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    for item in checklist:
        c.drawString(left + 0.3 * cm, y, f"☐ {item}")
        y -= 0.45 * cm
        if y < 2.5 * cm:
            c.showPage()
            y = _draw_header(c, "MySafar – Safety Tips & Checklist")

    y -= 0.2 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Safety tips")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    for t in tips:
        c.drawString(left + 0.3 * cm, y, f"• {t}")
        y -= 0.45 * cm
        if y < 2.5 * cm:
            c.showPage()
            y = _draw_header(c, "MySafar – Safety Tips & Checklist")

    return _finish_pdf(buf, c)

def make_invoice_pdf(
    trip: dict,
    traveler_name: str,
    selected_flight: dict | None,
    itinerary_rows: list[dict],
    fx_rate_to_mad: float,
    agency_fee_rate: float = 0.20,
) -> bytes:
    buf, c = _new_pdf()
    y = _draw_header(c, "MySafar – Invoice")

    width, height = A4
    left = 1.2 * cm

    # Header info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, f"Client/Traveler: {traveler_name}")
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    c.drawString(left, y, f"Trip: {trip['origin_city']} → {trip['destination_city']} ({trip['destination_country']})")
    y -= 0.5 * cm
    c.drawString(left, y, f"Dates: {trip['start_date']} → {trip['end_date']} | Type: {trip['travel_type']}")
    y -= 0.8 * cm

    # Flight amounts
    flight_amount = 0.0
    flight_currency = "MAD"
    flight_amount_mad = 0.0
    flight_line = "Flight: Not selected"

    if selected_flight:
        flight_amount = float(selected_flight.get("price_total") or 0)
        flight_currency = selected_flight.get("currency") or "MAD"
        flight_amount_mad = flight_amount * float(fx_rate_to_mad or 1.0)
        flight_line = f"Flight: {flight_amount:.2f} {flight_currency}  (≈ {flight_amount_mad:.2f} MAD @ rate {fx_rate_to_mad})"

    # Visits total (MAD)
    visits_total = sum(float(r.get("cost_mad") or 0) for r in itinerary_rows)

    subtotal_mad = flight_amount_mad + visits_total
    agency_fee = subtotal_mad * float(agency_fee_rate)
    grand_total = subtotal_mad + agency_fee

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Charges")
    y -= 0.6 * cm

    c.setFont("Helvetica", 10)
    c.drawString(left + 0.3 * cm, y, flight_line)
    y -= 0.45 * cm
    c.drawString(left + 0.3 * cm, y, f"Visits total: {visits_total:.2f} MAD")
    y -= 0.45 * cm
    c.drawString(left + 0.3 * cm, y, f"Subtotal: {subtotal_mad:.2f} MAD")
    y -= 0.45 * cm
    c.drawString(left + 0.3 * cm, y, f"Agency fee ({int(agency_fee_rate*100)}%): {agency_fee:.2f} MAD")
    y -= 0.45 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left + 0.3 * cm, y, f"TOTAL: {grand_total:.2f} MAD")
    y -= 0.8 * cm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y, "Visits breakdown")
    y -= 0.55 * cm
    c.setFont("Helvetica", 9)

    # List itinerary lines
    for r in itinerary_rows:
        line = f"{r['day_date']} {r['start_time'][:5]}–{r['end_time'][:5]} | {r['poi_name']} | {float(r.get('cost_mad') or 0):.2f} MAD"
        c.drawString(left + 0.3 * cm, y, line)
        y -= 0.38 * cm
        if y < 2.5 * cm:
            c.showPage()
            y = _draw_header(c, "MySafar – Invoice")
            c.setFont("Helvetica", 9)

    return _finish_pdf(buf, c)