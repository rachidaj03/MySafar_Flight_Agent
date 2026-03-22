import streamlit as st
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

@st.cache_data(ttl=30 * 24 * 3600)  # cache 30 days (important for usage policy)
def geocode_city(city: str, country: str | None = None) -> dict | None:
    """
    Returns {'lat': float, 'lon': float, 'display_name': str} or None.
    """
    q = city if not country else f"{city}, {country}"
    params = {"q": q, "format": "json", "limit": 1}

    headers = {
        # Identify your app (recommended by usage policy). Use your real domain/email later.
        "User-Agent": "MySafar/0.1 (contact@mysafar.ma)"
    }

    r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None

    top = data[0]
    return {
        "lat": float(top["lat"]),
        "lon": float(top["lon"]),
        "display_name": top.get("display_name", ""),
    }