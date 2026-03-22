from services.supabase_client import get_supabase, hydrate_supabase_session

def list_itinerary(trip_id: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    return (
        supabase.table("itinerary_items")
        .select("*")
        .eq("trip_id", trip_id)
        .order("day_date", desc=False)
        .order("start_time", desc=False)
        .execute()
    )

def delete_itinerary(trip_id: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    return supabase.table("itinerary_items").delete().eq("trip_id", trip_id).execute()

def insert_itinerary(user_id: str, trip_id: str, rows: list[dict]):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    payload = []
    for r in rows:
        payload.append({
            "user_id": user_id,
            "trip_id": trip_id,
            **r,
        })
    return supabase.table("itinerary_items").insert(payload).execute()