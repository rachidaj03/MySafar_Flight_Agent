import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="MySafar",
    page_icon="✈️",
    layout="wide"
)

st.markdown(
    """
    <style>
      .mysafar-header {
        display:flex;
        align-items:center;
        gap:16px;
        margin-top:6px;
        margin-bottom:8px;
      }
      .mysafar-title {
        font-size:32px;
        font-weight:800;
        margin:0;
        line-height:1.1;
      }
      .mysafar-subtitle {
        margin:0;
        opacity:0.85;
        font-size:14px;
      }
      .mysafar-card {
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(77,163,255,0.25);
        padding: 16px;
        border-radius: 16px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

logo_path = Path("assets/logo.png")
cols = st.columns([1, 5])
with cols[0]:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.info("Add your logo at assets/logo.png")

with cols[1]:
    st.markdown(
        """
        <div class="mysafar-header">
          <div>
            <p class="mysafar-title">MySafar</p>
            <p class="mysafar-subtitle">Your Morocco-first travel agency assistant ✈️</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div class="mysafar-card">
      <b>Status:</b> UI skeleton ready <br>
      Next: we will implement Login/Signup using Supabase Auth.
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("Use the left sidebar to navigate pages.")