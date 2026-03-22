import streamlit as st
from services.auth import sign_in, sign_up, sign_out, get_current_user

st.title("Login / Create Account")
user = get_current_user()
if user is not None:
    email = getattr(user, "email", None) or (user.get("email") if isinstance(user, dict) else None)
    st.success(f"You are logged in as: {email or 'user'}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log out"):
            sign_out()
            st.rerun()
    with col2:
        st.page_link("pages/2_Profiles.py", label="Go to Profiles", icon="👤")
    st.stop()

mode = st.radio("Mode", ["Login", "Sign up"], horizontal=True)
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Continue"):
    if mode == "Sign up":
        ok, msg = sign_up(email, password)
    else:
        ok, msg = sign_in(email, password)

    if ok:
        st.success(msg)
        st.rerun()
    else:
        st.error(msg)