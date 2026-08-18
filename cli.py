"""umbra -- which solar and lunar eclipses can you see from a location?"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eclipse.ephemeris import Ephemeris
from eclipse.circumstances import local_timeline
from eclipse.observer import solar_circumstances
from eclipse import db


def _in_range(row, y0, y1):
    y = int(row["peak_utc"][:4])
    return (y0 is None or y >= y0) and (y1 is None or y < y1)


def main():
    p = argparse.ArgumentParser(description="Eclipses visible from a location, solar and lunar.")
    p.add_argument("--lat", type=float, required=True, help="latitude, N positive")
    p.add_argument("--lon", type=float, required=True, help="longitude, E positive")
    p.add_argument("--from", dest="year_from", type=int, default=None)
    p.add_argument("--to", dest="year_to", type=int, default=None)
    p.add_argument("--all", action="store_true", help="include eclipses not visible from here")
    p.add_argument("--db", default="data/eclipses.db")
    args = p.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"No catalogue at {args.db}. Build it with scripts/build_catalog.py")

    eph = Ephemeris()
    conn = db.connect(args.db)
    events = []   # (jd_tt, line, visible)

    for row in db.all_eclipses(conn):
        if not _in_range(row, args.year_from, args.year_to):
            continue
        tl = local_timeline(eph, row, args.lat, args.lon)
        line = f"{row['peak_utc'][:10]}  Lunar {row['kind']:9}  ->  {tl['verdict']}"
        events.append((row["peak_jd_tt"], line, tl["verdict"] != "not visible"))

    for row in db.all_solar_eclipses(conn):
        if not _in_range(row, args.year_from, args.year_to):
            continue
        c = solar_circumstances(eph, eph.ts.tt_jd(row["peak_jd_tt"]), args.lat, args.lon)
        kind = c["kind"]
        if kind in ("Total", "Annular"):
            detail = f"{kind} here, mag {c['magnitude']:.2f}"
            if c.get("duration_s"):
                s = c["duration_s"]
                detail += f", {s // 60}m{s % 60:02d}s"
            visible = True
        elif kind == "Partial":
            detail = f"partial here, mag {c['magnitude']:.2f}"
            visible = True
        else:
            detail = "not visible from here"
            visible = False
        line = f"{row['peak_utc'][:10]}  Solar {row['kind']:9}  ->  {detail}"
        events.append((row["peak_jd_tt"], line, visible))

    events.sort(key=lambda e: e[0])
    header = f"Eclipses from lat {args.lat}, lon {args.lon}"
    print(header)
    print("=" * len(header))
    shown = 0
    for _, line, visible in events:
        if not args.all and not visible:
            continue
        shown += 1
        print(line)
    print(f"\n{shown} eclipse(s).")
    conn.close()


if __name__ == "__main__":
    main()