import streamlit as st
import pandas as pd
from datetime import date
from services.guard import require_login
from services.db_profiles import list_profiles
from services.db_trips import list_trips, create_trip, delete_trip, is_overlap_error, ranges_overlap

ctx = require_login()
user = ctx["user"]
user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

st.title("New Trip")
st.caption("Create trips per traveler profile. Trips cannot overlap for the same traveler.")

# ---- Load profiles
pres = list_profiles()
profiles = pres.data or []

if not profiles:
    st.warning("No traveler profiles found. Create one first in Profiles.")
    st.page_link("pages/2_Profiles.py", label="➡️ Go to Profiles", icon="👤")
    st.stop()

# Build select options
profile_label_to_id = {
    f"{p['full_name']} • {p['profile_type']}": p["id"]
    for p in profiles
}
profile_label = st.selectbox("Choose traveler profile *", list(profile_label_to_id.keys()))
profile_id = profile_label_to_id[profile_label]

# ---- Show existing trips for this profile
st.subheader("Existing trips for this traveler")
tres = list_trips(profile_id=profile_id)
existing = tres.data or []

if existing:
    df = pd.DataFrame([{
        "Start": t["start_date"],
        "End": t["end_date"],
        "From": t["origin_city"],
        "To": f"{t['destination_city']} ({t['destination_country']})",
        "Type": t["travel_type"],
    } for t in existing])
    st.dataframe(df, use_container_width=True)

    with st.expander("Delete a trip"):
        trip_options = {
            f"{t['start_date']} → {t['end_date']} | {t['origin_city']} → {t['destination_city']} ({t['travel_type']})": t["id"]
            for t in existing
        }
        choice = st.selectbox("Select trip to delete", list(trip_options.keys()))
        if st.button("Delete selected trip"):
            delete_trip(trip_options[choice])
            st.success("Trip deleted ✅")
            st.rerun()
else:
    st.info("No trips yet for this traveler.")

st.divider()

# ---- Trip creation form
st.subheader("Create a new trip")

with st.form("create_trip_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        origin_city = st.text_input("Origin city *", value="Casablanca")
        destination_city = st.text_input("Destination city *")
        destination_country = st.text_input("Destination country *", value="Morocco")

    with c2:
        travel_type = st.selectbox("Travel type *", ["budget", "standard", "business", "luxury"])
        start = st.date_input("Start date *", value=date.today())
        end = st.date_input("End date *", value=date.today())

    with c3:
        priority = st.selectbox("Main priority", ["lowest_price", "shortest_duration", "best_convenience"])
        max_stops = st.slider("Max stops", 0, 2, 1)
        # simple availability model (we’ll use it later for itinerary)
        daily_window = st.selectbox("Daily visit window", ["daytime", "after_work"])

    agency_notes = st.text_area("Extra notes / constraints (optional)", height=80)

    submit = st.form_submit_button("Save trip")

if submit:
    # Basic validation
    if not origin_city.strip() or not destination_city.strip() or not destination_country.strip():
        st.error("Origin, destination city, and destination country are required.")
        st.stop()
    if end < start:
        st.error("End date must be after (or equal to) start date.")
        st.stop()

    # Friendly pre-check (DB is still the final authority)
    for t in existing:
        a_start = date.fromisoformat(t["start_date"])
        a_end = date.fromisoformat(t["end_date"])
        if ranges_overlap(start, end, a_start, a_end):
            st.error("This trip overlaps with an existing trip for this traveler. Choose different dates.")
            st.stop()

    preferences = {
        "priority": priority,
        "max_stops": int(max_stops),
        "daily_window": daily_window,
        "notes": agency_notes.strip() if agency_notes else "",
    }

    try:
        create_trip(
            user_id=user_id,
            profile_id=profile_id,
            origin_city=origin_city,
            destination_city=destination_city,
            destination_country=destination_country,
            travel_type=travel_type,
            start_date=start,
            end_date=end,
            preferences=preferences,
        )
        st.success("Trip saved ✅")
        st.rerun()
    except Exception as e:
        if is_overlap_error(e):
            st.error("This trip overlaps with an existing trip for this traveler. Choose different dates.")
        else:
            st.error(f"Failed to save trip: {e}")