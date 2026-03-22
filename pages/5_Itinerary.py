import streamlit as st
import pandas as pd

from services.guard import require_login
from services.db_trips import list_trips
from services.geocode_nominatim import geocode_city
from services.osm_overpass import fetch_pois
from services.itinerary_gen import generate_itinerary_items
from services.db_itinerary import list_itinerary, delete_itinerary, insert_itinerary

ctx = require_login()
user = ctx["user"]
user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

st.title("Itinerary")
st.caption("Generate visits using OSM POIs + opening hours when available. You can edit before saving.")

# ---- Pick trip
tres = list_trips()
trips = tres.data or []
if not trips:
    st.warning("No trips found. Create one first.")
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

prefs = trip.get("preferences") or {}
daily_window = prefs.get("daily_window", "daytime")
travel_type = trip.get("travel_type", "standard")

# ---- Existing itinerary
st.subheader("Saved itinerary")
saved = list_itinerary(trip_id).data or []
if saved:
    df_saved = pd.DataFrame(saved)[["day_date","start_time","end_time","poi_name","poi_category","cost_mad","opening_ok","opening_hours","address"]]
    st.dataframe(df_saved, use_container_width=True)

    colA, colB = st.columns([1, 2])
    with colA:
        if st.button("Delete saved itinerary"):
            delete_itinerary(trip_id)
            st.success("Deleted ✅")
            st.rerun()
else:
    st.info("No itinerary saved yet for this trip.")

st.divider()

# ---- Generation controls
st.subheader("Generate new itinerary")
c1, c2, c3 = st.columns(3)
with c1:
    visits_per_day = st.slider("Visits per day", 1, 5, 3)
with c2:
    radius_km = st.slider("Search radius (km)", 2, 20, 6)
with c3:
    # MVP: ask user to confirm destination timezone assumption
    timezone_note = st.selectbox("Destination timezone assumption", ["local", "Africa/Casablanca"], index=0)

if st.button("Generate itinerary (preview)"):
    geo = geocode_city(trip["destination_city"], trip["destination_country"])
    if not geo:
        st.error("Could not geocode destination city. Try a more specific city name.")
        st.stop()

    st.write(f"Geocoded: {geo['display_name']}")
    pois = fetch_pois(geo["lat"], geo["lon"], radius_m=int(radius_km * 1000), limit=120)

    if not pois:
        st.warning("No POIs found with current filters/radius.")
        st.stop()

    rows = generate_itinerary_items(
        trip_start=pd.to_datetime(trip["start_date"]).date(),
        trip_end=pd.to_datetime(trip["end_date"]).date(),
        travel_type=travel_type,
        daily_window=daily_window,
        pois=pois,
        visits_per_day=int(visits_per_day),
        timezone_note=timezone_note,
    )

    if not rows:
        st.warning("Could not build an itinerary with the current day window. Try fewer visits/day.")
        st.stop()

    st.success("Preview generated ✅ You can edit below, then save.")
    st.session_state["it_preview"] = rows

# ---- Preview + edit
preview = st.session_state.get("it_preview")
if preview:
    df = pd.DataFrame(preview)
    # friendly order
    df = df[[
        "day_date","start_time","end_time",
        "poi_name","poi_category","cost_mad",
        "opening_ok","opening_hours","address",
        "lat","lon","notes"
    ]]

    st.subheader("Preview (editable)")
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "cost_mad": st.column_config.NumberColumn("cost_mad", min_value=0, step=10),
            "opening_ok": st.column_config.CheckboxColumn("opening_ok"),
        }
    )

    warn = edited["opening_ok"].isna().sum()
    if warn:
        st.warning(f"{warn} visit(s) have unknown opening hours (missing/unparseable). Please verify manually.")

    if st.button("Save itinerary to Supabase"):
        # wipe old + insert new
        delete_itinerary(trip_id)
        rows_out = edited.to_dict(orient="records")
        insert_itinerary(user_id=user_id, trip_id=trip_id, rows=rows_out)
        st.success("Itinerary saved ✅")
        st.session_state.pop("it_preview", None)
        st.rerun()