from services.supabase_client import get_supabase, hydrate_supabase_session

def upsert_document(user_id: str, trip_id: str, doc_type: str, storage_path: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    payload = {
        "user_id": user_id,
        "trip_id": trip_id,
        "doc_type": doc_type,
        "storage_path": storage_path,
    }
    return supabase.table("documents").upsert(payload, on_conflict="trip_id,doc_type").execute()

def list_documents(trip_id: str):
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    return supabase.table("documents").select("*").eq("trip_id", trip_id).execute()