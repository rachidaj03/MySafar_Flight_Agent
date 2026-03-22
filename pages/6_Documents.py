import streamlit as st
import pandas as pd

from services.guard import require_login
from services.db_trips import list_trips
from services.db_itinerary import list_itinerary
from services.db_flights import get_selected_flight
from services.pdfs import make_invoice_pdf, make_program_pdf, make_safety_pdf
from services.storage_docs import upload_pdf, create_signed_url
from services.db_documents import upsert_document, list_documents

ctx = require_login()
user = ctx["user"]
user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

st.title("Documents")
st.caption("Generate PDFs: Program, Safety/Checklist, and Invoice. Download instantly, optionally save to cloud.")

# ---- pick trip
tres = list_trips()
trips = tres.data or []
if not trips:
    st.warning("No trips found.")
    st.page_link("pages/3_New_Trip.py", label="➡️ Go to New Trip", icon="🧳")
    st.stop()

def trip_label(t):
    prof = (t.get("profiles") or {})
    who = prof.get("full_name", "Traveler")
    return f"{t['start_date']}→{t['end_date']} | {who} | {t['destination_city']} ({t['travel_type']})"

labels = [trip_label(t) for t in trips]
choice = st.selectbox("Select a trip", labels)
trip = trips[labels.index(choice)]
trip_id = trip["id"]

traveler_name = (trip.get("profiles") or {}).get("full_name", "Traveler")

# ---- load data
it_rows = list_itinerary(trip_id).data or []
sf = None
try:
    sf = get_selected_flight(trip_id).data
except Exception:
    sf = None

st.subheader("Data readiness")
c1, c2 = st.columns(2)
with c1:
    st.write("✅ Trip selected")
    st.write("✅ Itinerary items:", len(it_rows))
with c2:
    st.write("Selected flight:", "✅" if sf else "❌ (go to Flights page to select one)")

st.divider()

# ---- FX + agency fee controls
st.subheader("Invoice settings")
flight_currency = (sf or {}).get("currency") if sf else "MAD"
if flight_currency and flight_currency != "MAD":
    st.info(f"Flight currency is {flight_currency}. Enter an exchange rate to MAD for invoice totals.")
fx_rate = st.number_input("FX rate: 1 flight currency → MAD", min_value=0.0001, value=1.0, step=0.1)
agency_fee_rate = st.number_input("Agency fee rate", min_value=0.0, max_value=0.9, value=0.20, step=0.01)

save_to_cloud = st.checkbox("Save generated PDFs to Supabase Storage (recommended)", value=True)

# ---- show existing saved docs (cloud)
st.subheader("Saved documents (cloud)")
docs = []
try:
    docs = list_documents(trip_id).data or []
except Exception:
    docs = []

if docs:
    for d in docs:
        url = create_signed_url(d["storage_path"], expires_in=3600)
        st.write(f"- **{d['doc_type']}** | {d['created_at']}")
        if url:
            st.link_button(f"Open {d['doc_type']} (1h link)", url)
else:
    st.info("No cloud documents saved yet for this trip.")

st.divider()

# ---- Generate buttons
st.subheader("Generate PDFs")

colA, colB, colC = st.columns(3)

with colA:
    if st.button("Generate Program PDF"):
        if not it_rows:
            st.error("No itinerary saved. Generate & save an itinerary first.")
        else:
            pdf_bytes = make_program_pdf(trip, traveler_name, it_rows)
            st.download_button("Download Program PDF", pdf_bytes, file_name="mysafar_program.pdf", mime="application/pdf")

            if save_to_cloud:
                path = upload_pdf(user_id, trip_id, "program", pdf_bytes)
                upsert_document(user_id, trip_id, "program", path)
                st.success("Saved to cloud ✅")

with colB:
    if st.button("Generate Safety/Checklist PDF"):
        pdf_bytes = make_safety_pdf(trip, traveler_name, trip.get("travel_type", "standard"))
        st.download_button("Download Safety PDF", pdf_bytes, file_name="mysafar_safety.pdf", mime="application/pdf")

        if save_to_cloud:
            path = upload_pdf(user_id, trip_id, "safety", pdf_bytes)
            upsert_document(user_id, trip_id, "safety", path)
            st.success("Saved to cloud ✅")

with colC:
    if st.button("Generate Invoice PDF"):
        if not sf:
            st.error("No selected flight. Go to Flights page and save a flight first.")
        else:
            pdf_bytes = make_invoice_pdf(
                trip=trip,
                traveler_name=traveler_name,
                selected_flight=sf,
                itinerary_rows=it_rows,
                fx_rate_to_mad=float(fx_rate),
                agency_fee_rate=float(agency_fee_rate),
            )
            st.download_button("Download Invoice PDF", pdf_bytes, file_name="mysafar_invoice.pdf", mime="application/pdf")

            if save_to_cloud:
                path = upload_pdf(user_id, trip_id, "invoice", pdf_bytes)
                upsert_document(user_id, trip_id, "invoice", path)
                st.success("Saved to cloud ✅")