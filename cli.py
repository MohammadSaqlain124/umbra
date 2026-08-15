"""Query the catalogue: which lunar eclipses were visible from a location?"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eclipse.ephemeris import Ephemeris
from eclipse.circumstances import local_circumstances
from eclipse import db


def main():
    p = argparse.ArgumentParser(description="Lunar eclipses visible from a location.")
    p.add_argument("--lat", type=float, required=True, help="latitude, N positive")
    p.add_argument("--lon", type=float, required=True, help="longitude, E positive")
    p.add_argument("--from", dest="year_from", type=int, default=None)
    p.add_argument("--to", dest="year_to", type=int, default=None)
    p.add_argument("--all", action="store_true", help="include below-horizon eclipses")
    p.add_argument("--db", default="data/eclipses.db")
    args = p.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"No catalogue at {args.db}. Build it first with scripts/build_catalog.py")

    eph = Ephemeris()
    conn = db.connect(args.db)

    shown = 0
    for row in db.all_eclipses(conn):
        year = int(row["peak_utc"][:4])
        if args.year_from and year < args.year_from:
            continue
        if args.year_to and year >= args.year_to:
            continue

        c = local_circumstances(eph, row, args.lat, args.lon)
        if not args.all and not c["visible"]:
            continue

        shown += 1
        tag = "visible" if c["visible"] else "(below horizon)"
        print(f"{c['peak_utc']}  {c['kind']:10} mag {c['umbral_magnitude']:6.2f}  "
              f"alt {c['moon_altitude_deg']:>6}\u00b0  {c['moon_direction']:>3}  {tag}")

    print(f"\n{shown} eclipse(s).")
    conn.close()


if __name__ == "__main__":
    main()