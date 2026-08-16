"""Local circumstances: was a given eclipse above your horizon?"""

from skyfield.searchlib import find_discrete
from eclipse.contacts import contact_times
from skyfield.api import wgs84

_COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def _compass(az_degrees):
    return _COMPASS[int((az_degrees % 360) / 22.5 + 0.5) % 16]


def local_circumstances(eph, eclipse_row, latitude, longitude):
    # The eclipse peak is one exact instant (stored as a TT Julian Date).
    # We ask: from this spot on Earth, where was the Moon at that instant?
    t = eph.ts.tt_jd(eclipse_row["peak_jd_tt"])

    site = wgs84.latlon(latitude, longitude)
    observer = eph.earth + site                      # you, standing on Earth
    app = observer.at(t).observe(eph.moon).apparent()
    alt, az, _ = app.altaz()                         # altitude & compass bearing

    return {
        "peak_utc": eclipse_row["peak_utc"],
        "kind": eclipse_row["kind"],
        "umbral_magnitude": round(eclipse_row["umbral_magnitude"], 3),
        "moon_altitude_deg": round(alt.degrees, 1),
        "moon_azimuth_deg": round(az.degrees, 1),
        "moon_direction": _compass(az.degrees),
        "visible": alt.degrees > 0,                  # above the horizon = you saw it
    }
    
def _altitude(site, moon, t):
    # Moon's altitude in degrees, seen from `site` at time(s) t.
    # Works for a single time or an array (find_discrete passes many).
    alt, _, _ = site.at(t).observe(moon).apparent().altaz()
    return alt.degrees


def local_timeline(eph, eclipse_row, latitude, longitude):
    # For each contact, is the Moon above this location's horizon? And if the
    # Moon rises or sets partway through, exactly when? This is the honest
    # answer Phase 1 couldn't give: a peak below the horizon no longer means
    # the whole eclipse was invisible.
    site = eph.earth + wgs84.latlon(latitude, longitude)
    moon = eph.moon

    contacts = contact_times(eph, eclipse_row["peak_jd_tt"])
    ordered = sorted(contacts.items(), key=lambda kv: kv[1].tt)

    rows = []
    for label, t in ordered:
        alt = float(_altitude(site, moon, t))
        rows.append({"label": label, "time": t,
                     "altitude_deg": round(alt, 1), "up": alt > 0})

    up_flags = [r["up"] for r in rows]
    if all(up_flags):
        verdict = "fully visible"
    elif any(up_flags):
        verdict = "partially visible"
    else:
        verdict = "not visible"

    # The exact horizon crossing(s) between first and last contact.
    def moon_up(t):
        return _altitude(site, moon, t) > 0
    moon_up.step_days = 0.01

    crossings = []
    p1, p4 = contacts.get("P1"), contacts.get("P4")
    if p1 is not None and p4 is not None:
        times, values = find_discrete(p1, p4, moon_up)
        for tc, v in zip(times, values):
            crossings.append({"time": tc, "rising": bool(v)})

    return {"kind": eclipse_row["kind"], "verdict": verdict,
            "contacts": rows, "crossings": crossings}