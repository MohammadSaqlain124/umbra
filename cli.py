"""umbra -- which solar and lunar eclipses can you see from a location?"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eclipse.ephemeris import Ephemeris
from eclipse.query import find_events
from eclipse import db


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
    events = find_events(eph, conn, args.lat, args.lon, args.year_from, args.year_to)
    conn.close()

    header = f"Eclipses from lat {args.lat}, lon {args.lon}"
    print(header)
    print("=" * len(header))
    shown = 0
    for e in events:
        if not args.all and not e["visible"]:
            continue
        shown += 1
        category = e["category"].capitalize()
        print(f"{e['date']}  {category} {e['kind']:9}  ->  {e['summary']}")
    print(f"\n{shown} eclipse(s).")


if __name__ == "__main__":
    main()