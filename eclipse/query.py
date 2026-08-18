"""Unified query: every eclipse visible from a location, solar and lunar.

Single source of truth shared by the CLI and the web API, so the two can never
disagree about what an observer would see.
"""

from eclipse.circumstances import local_timeline
from eclipse.observer import solar_circumstances
from eclipse import db


def _in_range(row, y0, y1):
    y = int(row["peak_utc"][:4])
    return (y0 is None or y >= y0) and (y1 is None or y < y1)


def find_events(eph, conn, latitude, longitude, year_from=None, year_to=None):
    events = []

    for row in db.all_eclipses(conn):
        if not _in_range(row, year_from, year_to):
            continue
        tl = local_timeline(eph, row, latitude, longitude)
        events.append({
            "date": row["peak_utc"][:10],
            "jd_tt": row["peak_jd_tt"],
            "category": "lunar",
            "kind": row["kind"],
            "visible": tl["verdict"] != "not visible",
            "summary": tl["verdict"],
        })

    for row in db.all_solar_eclipses(conn):
        if not _in_range(row, year_from, year_to):
            continue
        c = solar_circumstances(eph, eph.ts.tt_jd(row["peak_jd_tt"]), latitude, longitude)
        kind = c["kind"]
        event = {
            "date": row["peak_utc"][:10],
            "jd_tt": row["peak_jd_tt"],
            "category": "solar",
            "kind": row["kind"],
            "visible": kind in ("Total", "Annular", "Partial"),
            "seen_as": kind,
            "magnitude": c.get("magnitude"),
            "duration_s": c.get("duration_s"),
        }
        if kind in ("Total", "Annular"):
            s = c.get("duration_s")
            dur = f", {s // 60}m{s % 60:02d}s" if s else ""
            event["summary"] = f"{kind} here, mag {c['magnitude']:.2f}{dur}"
        elif kind == "Partial":
            event["summary"] = f"partial here, mag {c['magnitude']:.2f}"
        else:
            event["summary"] = "not visible from here"
        events.append(event)

    events.sort(key=lambda e: e["jd_tt"])
    return events