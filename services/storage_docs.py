from services.supabase_client import get_supabase, hydrate_supabase_session

BUCKET = "mysafar-docs"

def upload_pdf(user_id: str, trip_id: str, doc_type: str, pdf_bytes: bytes) -> str:
    """
    Uploads to: {user_id}/{trip_id}/{doc_type}.pdf
    Returns storage path.
    """
    supabase = get_supabase()
    hydrate_supabase_session(supabase)

    path = f"{user_id}/{trip_id}/{doc_type}.pdf"

    # Upload with upsert (overwrite)
    supabase.storage.from_(BUCKET).upload(
        path,
        pdf_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )
    return path

def create_signed_url(path: str, expires_in: int = 3600) -> str:
    supabase = get_supabase()
    hydrate_supabase_session(supabase)

    res = supabase.storage.from_(BUCKET).create_signed_url(path, expires_in)
    # supabase-py returns dict-like; be defensive:
    if isinstance(res, dict):
        return res.get("signedURL") or res.get("signed_url") or ""
    return getattr(res, "signedURL", "") or ""