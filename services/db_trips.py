import re
from datetime import date
import streamlit as st
from services.supabase_client import get_supabase, hydrate_supabase_session

def list_trips(profile_id: str | None = None):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)

    q = supabase.table("trips").select("*,profiles(full_name,profile_type)")
    if profile_id:
        q = q.eq("profile_id", profile_id)

    return q.order("start_date", desc=False).execute()

def create_trip(
    user_id: str,
    profile_id: str,
    origin_city: str,
    destination_city: str,
    destination_country: str,
    travel_type: str,
    start_date: date,
    end_date: date,
    preferences: dict,
):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)

    payload = {
        "user_id": user_id,
        "profile_id": profile_id,
        "origin_city": origin_city.strip(),
        "destination_city": destination_city.strip(),
        "destination_country": destination_country.strip(),
        "travel_type": travel_type,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "preferences": preferences or {},
    }
    return supabase.table("trips").insert(payload).execute()

def delete_trip(trip_id: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    return supabase.table("trips").delete().eq("id", trip_id).execute()

def is_overlap_error(err: Exception) -> bool:
    msg = str(err).lower()
    # Postgres constraint name or overlap operator message
    return ("trips_no_overlap" in msg) or ("exclude constraint" in msg) or ("conflicting key" in msg)

def ranges_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    # inclusive overlap
    return not (a_end < b_start or b_end < a_start)