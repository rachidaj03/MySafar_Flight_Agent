import streamlit as st
import requests

BASE_URL = "https://api.duffel.com"

def _headers() -> dict:
    return {
        "Authorization": f"Bearer {st.secrets['DUFFEL_ACCESS_TOKEN']}",
        "Duffel-Version": st.secrets.get("DUFFEL_API_VERSION", "v2"),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }

def create_offer_request(
    origin_iata: str,
    destination_iata: str,
    departure_date: str,
    return_date: str | None,
    adults: int = 1,
    cabin_class: str | None = None,
    max_connections: int | None = None,
    supplier_timeout_ms: int | None = 20000,
) -> dict:
    """
    Creates an offer request. We'll then list offers separately (so we can sort/filter).
    """
    passengers = [{"type": "adult"} for _ in range(int(adults))]

    slices = [{"origin": origin_iata, "destination": destination_iata, "departure_date": departure_date}]
    if return_date:
        slices.append({"origin": destination_iata, "destination": origin_iata, "departure_date": return_date})

    data = {"slices": slices, "passengers": passengers}
    if cabin_class:
        data["cabin_class"] = cabin_class
    if max_connections is not None:
        data["max_connections"] = int(max_connections)

    params = {"return_offers": "false"}  # list offers separately
    if supplier_timeout_ms:
        params["supplier_timeout"] = int(supplier_timeout_ms)

    r = requests.post(f"{BASE_URL}/air/offer_requests", headers=_headers(), params=params, json={"data": data}, timeout=60)
    r.raise_for_status()
    return r.json()["data"]

def list_offers(offer_request_id: str, limit: int = 50, sort: str = "total_amount", max_connections: int | None = None) -> list[dict]:
    """
    GET /air/offers supports sorting by total_amount or total_duration, and filtering by max_connections.
    """
    params = {
        "offer_request_id": offer_request_id,
        "limit": int(limit),
        "sort": sort,  # "total_amount" or "total_duration"
    }
    if max_connections is not None:
        params["max_connections"] = int(max_connections)

    r = requests.get(f"{BASE_URL}/air/offers", headers=_headers(), params=params, timeout=60)
    r.raise_for_status()
    return r.json()["data"]