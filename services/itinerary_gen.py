from datetime import date, datetime, time, timedelta
import humanized_opening_hours as hoh

DEFAULT_COSTS_MAD = {
    "museum": 120,
    "gallery": 80,
    "attraction": 100,
    "viewpoint": 0,
    "historic": 40,
    "park": 0,
    "theatre": 150,
    "poi": 50,
}

DEFAULT_DURATIONS_MIN = {
    "museum": 90,
    "gallery": 60,
    "attraction": 75,
    "viewpoint": 45,
    "historic": 60,
    "park": 60,
    "theatre": 90,
    "poi": 60,
}

def daterange_inclusive(d1: date, d2: date):
    cur = d1
    while cur <= d2:
        yield cur
        cur += timedelta(days=1)

def pick_window(daily_window: str, travel_type: str):
    # business travel: after_work by default
    if travel_type == "business":
        return time(18, 0), time(21, 0)
    if daily_window == "after_work":
        return time(18, 0), time(21, 0)
    return time(10, 0), time(18, 0)

def add_minutes(t: time, minutes: int) -> time:
    dt = datetime(2000, 1, 1, t.hour, t.minute) + timedelta(minutes=minutes)
    return dt.time()

def normalize_category(cat: str | None) -> str:
    if not cat:
        return "poi"
    c = cat.lower()
    for k in ["museum", "gallery", "attraction", "viewpoint", "historic", "park", "theatre"]:
        if k in c:
            return k
    return "poi"

def opening_ok(opening_hours: str | None, check_dt: datetime) -> bool | None:
    """
    Returns:
      True/False if opening_hours present and parseable
      None if missing or unparseable
    """
    if not opening_hours:
        return None
    try:
        oh = hoh.OHParser(opening_hours)
        return bool(oh.is_open(check_dt))
    except Exception:
        return None

def generate_itinerary_items(
    trip_start: date,
    trip_end: date,
    travel_type: str,
    daily_window: str,
    pois: list[dict],
    visits_per_day: int = 3,
    timezone_note: str = "local",
) -> list[dict]:
    """
    Produces itinerary rows for insertion into Supabase.
    """
    items = []
    if not pois:
        return items

    day_start_t, day_end_t = pick_window(daily_window, travel_type)
    buffer_min = 20

    poi_idx = 0
    for d in daterange_inclusive(trip_start, trip_end):
        cur_t = day_start_t
        added = 0

        while added < visits_per_day and poi_idx < len(pois):
            p = pois[poi_idx]
            poi_idx += 1

            cat = normalize_category(p.get("category"))
            dur = DEFAULT_DURATIONS_MIN.get(cat, 60)
            start_t = cur_t
            end_t = add_minutes(start_t, dur)

            # stop if we overflow the daily window
            if end_t > day_end_t:
                break

            # check opening hours at the planned start time (best-effort)
            check_dt = datetime(d.year, d.month, d.day, start_t.hour, start_t.minute)
            ok = opening_ok(p.get("opening_hours"), check_dt)

            items.append({
                "day_date": str(d),
                "start_time": start_t.strftime("%H:%M:%S"),
                "end_time": end_t.strftime("%H:%M:%S"),
                "poi_name": p["name"],
                "poi_category": cat,
                "address": p.get("address"),
                "lat": p.get("lat"),
                "lon": p.get("lon"),
                "opening_hours": p.get("opening_hours"),
                "opening_ok": ok,
                "cost_mad": float(DEFAULT_COSTS_MAD.get(cat, 50)),
                "notes": f"Timezone assumed: {timezone_note}",
            })

            # move time forward: duration + buffer
            cur_t = add_minutes(end_t, buffer_min)
            added += 1

    return items