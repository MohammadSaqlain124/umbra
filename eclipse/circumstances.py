"""Local circumstances: which phases of a lunar eclipse were visible from a
location, and when the Moon crossed the horizon."""

from skyfield.api import wgs84
from skyfield.searchlib import find_discrete
from eclipse.contacts import contact_times


def _altitude(site, moon, t):
    # Moon's altitude in degrees, seen from `site` at time(s) t.
    alt, _, _ = site.at(t).observe(moon).apparent().altaz()
    return alt.degrees


def local_timeline(eph, eclipse_row, latitude, longitude):
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