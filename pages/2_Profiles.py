import streamlit as st
from services.guard import require_login
from services.db_profiles import list_profiles, create_profile, delete_profile, mask_sensitive

ctx = require_login()
user = ctx["user"]

user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

st.title("Profiles")
st.caption("Create traveler profiles")

st.subheader("Add a profile")

with st.form("add_profile_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 1])

    with col1:
        profile_type = st.selectbox("Relationship type", ["Myself", "Family", "Friend"])
        full_name = st.text_input("Full name *")
        birth_date = st.date_input("Birth date", value=None,max_value = "today",min_value ="1900-01-01")

    with col2:
        passport_number = st.text_input("Passport number")
        visa_number = st.text_input("Visa number (If Visa is required)")
        notes = st.text_area("Notes (optional)", height=100)

    submitted = st.form_submit_button("Save profile")

if submitted:
    if not full_name.strip():
        st.error("Full name is required.")
    else:
        try:
            res = create_profile(
                user_id=user_id,
                profile_type=profile_type,
                full_name=full_name,
                birth_date=birth_date,
                passport_number=passport_number,
                visa_number=visa_number,
                notes=notes,
            )
            if getattr(res, "data", None) is None:
                st.error("Insert failed (no data returned).")
            else:
                st.success("Profile saved")
                st.rerun()
        except Exception as e:
            st.error(f"Error saving profile: {e}")

st.divider()
st.subheader("Your saved profiles")

try:
    res = list_profiles()
    rows = res.data or []
except Exception as e:
    st.error(f"Error loading profiles: {e}")
    rows = []

if not rows:
    st.info("No profiles yet. Add your first profile above.")
else:
    for p in rows:
        title = f"{p['full_name']}  •  {p['profile_type']}"
        with st.expander(title, expanded=False):
            c1, c2, c3 = st.columns([2, 2, 1])

            with c1:
                st.write(f"**Birth date:** {p.get('birth_date') or '-'}")
                st.write(f"**Notes:** {p.get('notes') or '-'}")

            with c2:
                st.write(f"**Passport:** {mask_sensitive(p.get('passport_number')) or '-'}")
                st.write(f"**Visa:** {mask_sensitive(p.get('visa_number')) or '-'}")

            with c3:
                if st.button("Delete", key=f"del_{p['id']}"):
                    try:
                        delete_profile(p["id"])
                        st.success("Deleted")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")