import streamlit as st
from services.supabase_client import get_supabase, hydrate_supabase_session

def _clear_auth_state() -> None:
    for k in ["user", "access_token", "refresh_token"]:
        if k in st.session_state:
            del st.session_state[k]

def get_current_user():
    supabase = get_supabase()
    hydrate_supabase_session(supabase)

    jwt = st.session_state.get("access_token")
    if not jwt:
        return None

    try:
        # get_user(jwt) validates the JWT on the server
        res = supabase.auth.get_user(jwt)
        # res.user is typical, but be defensive
        return getattr(res, "user", None) or res.get("user")
    except Exception:
        _clear_auth_state()
        return None

def sign_up(email: str, password: str) -> tuple[bool, str]:
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        # If email confirmation is ON, session may be None until user confirms
        session = getattr(res, "session", None)
        user = getattr(res, "user", None)

        if session is not None:
            st.session_state["access_token"] = session.access_token
            st.session_state["refresh_token"] = session.refresh_token
            st.session_state["user"] = user
            return True, "Account created and logged in"
        return True, "Account created (Check email to confirm if confirmation is enabled)"
    except Exception as e:
        return False, f"Signup failed: {e}"

def sign_in(email: str, password: str) -> tuple[bool, str]:
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session = res.session
        user = res.user

        st.session_state["access_token"] = session.access_token
        st.session_state["refresh_token"] = session.refresh_token
        st.session_state["user"] = user
        return True, "Logged in"
    except Exception as e:
        return False, f"Login failed: {e}"

def sign_out() -> None:
    supabase = get_supabase()
    hydrate_supabase_session(supabase)
    try:
        supabase.auth.sign_out()
    finally:
        _clear_auth_state()