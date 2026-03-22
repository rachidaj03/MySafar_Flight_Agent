import re

_DUR_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?")

def parse_iso_duration_minutes(s: str | None) -> int:
    if not s:
        return 0
    m = _DUR_RE.fullmatch(s)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    return 60 * h + mins

def summarize_duffel_offer(offer: dict) -> dict:
    price = float(offer.get("total_amount") or 0)
    currency = offer.get("total_currency") or ""

    slices = offer.get("slices") or []
    minutes = sum(parse_iso_duration_minutes(sl.get("duration")) for sl in slices)

    stops = 0
    carriers = set()
    for sl in slices:
        segs = sl.get("segments") or []
        stops += max(0, len(segs) - 1)
        for seg in segs:
            op = seg.get("operating_carrier") or {}
            cc = op.get("iata_code")
            if cc:
                carriers.add(cc)

    return {
        "price": price,
        "currency": currency,
        "minutes": minutes,
        "stops": stops,
        "carriers": sorted(list(carriers)),
    }

def offer_matches_partner(offer: dict, allowed_carriers: set[str]) -> bool:
    if not allowed_carriers:
        return True
    s = summarize_duffel_offer(offer)
    return bool(set(s["carriers"]) & allowed_carriers)

def score_offers(offers: list[dict], priority: str) -> list[tuple[float, dict, dict]]:
    summaries = [summarize_duffel_offer(o) for o in offers]
    if not summaries:
        return []

    prices = [s["price"] for s in summaries]
    mins = [s["minutes"] for s in summaries]
    stops = [s["stops"] for s in summaries]

    pmin, pmax = min(prices), max(prices)
    tmin, tmax = min(mins), max(mins)
    smin, smax = min(stops), max(stops)

    def norm(x, a, b):
        if a == b:
            return 0.0
        return (x - a) / (b - a)

    if priority == "lowest_price":
        w_price, w_time, w_stops = 0.60, 0.25, 0.15
    elif priority == "shortest_duration":
        w_price, w_time, w_stops = 0.25, 0.60, 0.15
    else:  # best_convenience
        w_price, w_time, w_stops = 0.25, 0.25, 0.50

    scored = []
    for offer, s in zip(offers, summaries):
        pn = norm(s["price"], pmin, pmax)
        tn = norm(s["minutes"], tmin, tmax)
        sn = norm(s["stops"], smin, smax)

        score = (w_price * (1 - pn)) + (w_time * (1 - tn)) + (w_stops * (1 - sn))
        scored.append((score, offer, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored