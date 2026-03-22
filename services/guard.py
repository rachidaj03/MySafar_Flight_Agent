import streamlit as st
from services.auth import get_current_user

def require_login() -> dict:
    user = get_current_user()
    if user is None:
        st.warning("You must log in to access this page.")
        st.page_link("pages/1_Login.py", label="➡️ Go to Login", icon="🔐")
        st.stop()

    # user is usually an object with .email, but we keep it flexible
    email = getattr(user, "email", None) or user.get("email") if isinstance(user, dict) else None
    st.sidebar.success(f"Logged in as: {email or 'user'}")
    return {"user": user, "email": email}