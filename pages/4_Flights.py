import streamlit as st
from services.guard import require_login
from services.db_trips import list_trips
from services.duffel_client import create_offer_request, list_offers
from services.flight_scoring_duffel import score_offers, offer_matches_partner
from services.db_flights import save_selected_flight, get_selected_flight

ctx = require_login()
user = ctx["user"]
user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

st.title("Flights (Duffel)")

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
    return f"{t['start_date']}→{t['end_date']} | {who} | {t['origin_city']} → {t['destination_city']} ({t['travel_type']})"

labels = [trip_label(t) for t in trips]
choice = st.selectbox("Select a trip", labels)
trip = trips[labels.index(choice)]
trip_id = trip["id"]
prefs = trip.get("preferences") or {}
priority = prefs.get("priority", "lowest_price")
max_stops_pref = int(prefs.get("max_stops", 1))

# ---- Partner airline preference (your rules)
destination_country = (trip.get("destination_country") or "").strip().lower()
travel_type = trip.get("travel_type")

DOMESTIC = {"3O", "AT"}
STANDARD_INTL = {"AT"}
BUDGET_EU = {"AT", "FR", "3O"}
LUXURY = {"AT", "AF"}

if destination_country == "morocco":
    default_allowed = DOMESTIC
elif travel_type == "luxury":
    default_allowed = LUXURY
elif travel_type in ("budget", "standard"):
    default_allowed = BUDGET_EU
else:
    default_allowed = STANDARD_INTL

use_partner_filter = st.checkbox("Prefer partner airlines first", value=True)
allowed = default_allowed if use_partner_filter else set()

# ---- Inputs (IATA codes)
st.subheader("Route")
c1, c2 = st.columns(2)
with c1:
    origin_iata = st.text_input("Origin IATA (e.g., CMN, RAK, FEZ)", value="CMN").strip().upper()
with c2:
    dest_iata = st.text_input("Destination IATA (e.g., CDG, BCN, LIS)", value="").strip().upper()

st.subheader("Passengers & options")
c3, c4, c5 = st.columns(3)
with c3:
    adults = st.number_input("Adults", min_value=1, max_value=9, value=1, step=1)
with c4:
    round_trip = st.checkbox("Round trip", value=True)
with c5:
    cabin_class = st.selectbox("Cabin class", [None, "economy", "premium_economy", "business", "first"], index=0)

max_connections = st.slider("Max connections (stops)", 0, 2, min(max_stops_pref, 2))

# Trip dates
departure_date = trip["start_date"]
return_date = trip["end_date"] if round_trip else None

# ---- Show current selected flight
try:
    current = get_selected_flight(trip_id).data
except Exception:
    current = None

if current:
    st.success(
        f"Selected flight saved ✅  \n"
        f"Price: **{current.get('price_total')} {current.get('currency')}** | "
        f"Stops: **{current.get('total_stops')}** | "
        f"Duration: **{current.get('total_duration_minutes')} min**"
    )

# --- add near the top of flights.py (after trip_id is known)
if "top_offers" not in st.session_state:
    st.session_state["top_offers"] = None   # list of (label, offer)

# ---- Search
if st.button("Search flights"):
    if len(origin_iata) != 3 or len(dest_iata) != 3:
        st.error("Please enter valid 3-letter IATA codes for origin and destination.")
        st.stop()

    try:
        orq = create_offer_request(
            origin_iata=origin_iata,
            destination_iata=dest_iata,
            departure_date=departure_date,
            return_date=return_date,
            adults=int(adults),
            cabin_class=cabin_class,
            max_connections=int(max_connections),
        )
        offers = list_offers(
            offer_request_id=orq["id"],
            limit=50,
            sort="total_amount",
            max_connections=int(max_connections),
        )
    except Exception as e:
        st.error(f"Duffel search failed: {e}")
        st.stop()

    if not offers:
        st.warning("No offers returned. Try different IATA codes/dates or increase max connections.")
        st.session_state["top_offers"] = None
        st.stop()

    # partner-first filter
    filtered = [o for o in offers if offer_matches_partner(o, allowed)] if allowed else offers
    if allowed and not filtered:
        st.warning("No offers matched partner airlines. Showing ALL airlines instead.")
        filtered = offers

    ranked = score_offers(filtered, priority=priority)
    top = ranked[:10]

    # Build display labels + keep the offer objects
    top_offers = []
    for idx, (sc, offer, s) in enumerate(top, start=1):
        hrs = round(s["minutes"] / 60, 1) if s["minutes"] else 0
        carriers = ",".join(s["carriers"][:5])
        label = f"#{idx} | {s['price']} {s['currency']} | {hrs}h | stops={s['stops']} | carriers={carriers} | score={sc:.3f}"
        top_offers.append((label, offer))

    st.session_state["top_offers"] = top_offers
    st.success("Offers loaded ✅ Scroll down to choose and save.")

# ---- Always show offers if we have them in session_state
top_offers = st.session_state.get("top_offers")
if top_offers:
    st.subheader("Top offers (ranked)")

    labels = [x[0] for x in top_offers]
    pick_label = st.radio("Choose an offer to save", labels, key="offer_pick_label")

    chosen_offer = dict(top_offers)[pick_label]

    if st.button("Save selected flight for this trip", key="save_selected_offer"):
        try:
            if not user_id:
                st.error("user_id is None (login/session issue).")
                st.stop()

            res = save_selected_flight(user_id=user_id, trip_id=trip_id, offer=chosen_offer)
            # Optional debug:
            # st.write("DB response:", res.data)

            st.success("Saved ✅")
            st.rerun()
        except Exception as e:
            st.error(f"Save failed: {e}")