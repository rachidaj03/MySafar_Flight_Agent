import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    """
    Cached Supabase client (keeps the same object across Streamlit reruns).
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

def hydrate_supabase_session(supabase: Client) -> None:
    """
    Re-attach the session to the Supabase client on every rerun.
    Needed so calls run in the logged-in user's context.
    """
    access = st.session_state.get("access_token")
    refresh = st.session_state.get("refresh_token")
    if access and refresh:
        supabase.auth.set_session(access, refresh)