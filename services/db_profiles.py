import streamlit as st
from services.supabase_client import get_supabase, hydrate_supabase_session

def list_profiles():
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    # RLS already limits to current user, but selecting all is fine
    return supabase.table("profiles").select("*").order("created_at", desc=True).execute()

def create_profile(user_id: str, profile_type: str, full_name: str, birth_date, passport_number: str, visa_number: str, notes: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)

    payload = {
        "user_id": user_id,
        "profile_type": profile_type,
        "full_name": full_name.strip(),
        "birth_date": str(birth_date) if birth_date else None,
        "passport_number": passport_number.strip() if passport_number else None,
        "visa_number": visa_number.strip() if visa_number else None,
        "notes": notes.strip() if notes else None,
    }
    return supabase.table("profiles").insert(payload).execute()

def delete_profile(profile_id: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    return supabase.table("profiles").delete().eq("id", profile_id).execute()

def mask_sensitive(s: str | None) -> str:
    if not s:
        return ""
    s = s.strip()
    if len(s) <= 4:
        return "****"
    return "*" * (len(s) - 4) + s[-4:]