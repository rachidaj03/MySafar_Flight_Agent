import streamlit as st
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

@st.cache_data(ttl=6 * 3600)
def fetch_pois(lat: float, lon: float, radius_m: int = 6000, limit: int = 60) -> list[dict]:
    """
    Returns a list of POIs with tags from OSM around (lat, lon).
    """
    # A practical POI set for travel itineraries:
    # tourism=attraction|museum|gallery|viewpoint, historic=*, leisure=park, amenity=theatre
    query = f"""
    [out:json][timeout:25];
    (
      node(around:{radius_m},{lat},{lon})["tourism"~"attraction|museum|gallery|viewpoint"];
      way(around:{radius_m},{lat},{lon})["tourism"~"attraction|museum|gallery|viewpoint"];
      relation(around:{radius_m},{lat},{lon})["tourism"~"attraction|museum|gallery|viewpoint"];

      node(around:{radius_m},{lat},{lon})["historic"];
      way(around:{radius_m},{lat},{lon})["historic"];
      relation(around:{radius_m},{lat},{lon})["historic"];

      node(around:{radius_m},{lat},{lon})["leisure"="park"];
      way(around:{radius_m},{lat},{lon})["leisure"="park"];
      relation(around:{radius_m},{lat},{lon})["leisure"="park"];

      node(around:{radius_m},{lat},{lon})["amenity"="theatre"];
      way(around:{radius_m},{lat},{lon})["amenity"="theatre"];
      relation(around:{radius_m},{lat},{lon})["amenity"="theatre"];
    );
    out center tags;
    """

    r = requests.post(OVERPASS_URL, data=query.encode("utf-8"), timeout=60)
    r.raise_for_status()
    js = r.json()
    els = js.get("elements", []) or []

    pois = []
    for e in els:
        tags = e.get("tags", {}) or {}
        name = tags.get("name") or tags.get("name:en")
        if not name:
            continue

        if "lat" in e and "lon" in e:
            plat, plon = e["lat"], e["lon"]
        else:
            c = e.get("center") or {}
            plat, plon = c.get("lat"), c.get("lon")

        if plat is None or plon is None:
            continue

        category = (
            tags.get("tourism")
            or tags.get("historic")
            or tags.get("leisure")
            or tags.get("amenity")
            or "poi"
        )

        address = " ".join([
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:suburb", ""),
            tags.get("addr:city", ""),
        ]).strip()

        pois.append({
            "name": name,
            "category": category,
            "lat": float(plat),
            "lon": float(plon),
            "opening_hours": tags.get("opening_hours"),
            "address": address if address else None,
        })

    # De-duplicate by name (simple MVP rule)
    seen = set()
    uniq = []
    for p in pois:
        key = p["name"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)

    return uniq[:limit]