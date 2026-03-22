from services.supabase_client import get_supabase, hydrate_supabase_session
from services.flight_scoring_duffel import summarize_duffel_offer

def get_selected_flight(trip_id: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    return (
        supabase.table("selected_flights")
        .select("*")
        .eq("trip_id", trip_id)
        .maybe_single()
        .execute()
    )

def save_selected_flight(user_id: str, trip_id: str, offer: dict):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    s = summarize_duffel_offer(offer)
    payload = {
        "user_id": user_id,
        "trip_id": trip_id,
        "offer_json": offer,
        "price_total": s["price"],
        "currency": s["currency"],
        "total_duration_minutes": s["minutes"],
        "total_stops": s["stops"],
        "validating_carriers": s["carriers"],
    }
    return supabase.table("selected_flights").upsert(payload, on_conflict="trip_id").execute()