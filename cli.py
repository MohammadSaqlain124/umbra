"""Query the catalogue: which lunar eclipses were visible from a location?"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eclipse.ephemeris import Ephemeris
from eclipse.circumstances import local_timeline
from eclipse import db


def _crossing_note(tl):
    # Turn any horizon crossing into a short parenthetical for the summary.
    notes = []
    for c in tl["crossings"]:
        verb = "rises" if c["rising"] else "sets"
        notes.append(f"Moon {verb} {c['time'].utc_strftime('%H:%M')} UTC")
    return f"   ({'; '.join(notes)})" if notes else ""


def main():
    p = argparse.ArgumentParser(description="Lunar eclipses visible from a location.")
    p.add_argument("--lat", type=float, required=True, help="latitude, N positive")
    p.add_argument("--lon", type=float, required=True, help="longitude, E positive")
    p.add_argument("--from", dest="year_from", type=int, default=None)
    p.add_argument("--to", dest="year_to", type=int, default=None)
    p.add_argument("--all", action="store_true", help="include not-visible eclipses")
    p.add_argument("--timeline", action="store_true", help="print all seven contacts")
    p.add_argument("--db", default="data/eclipses.db")
    args = p.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"No catalogue at {args.db}. Build it with scripts/build_catalog.py")

    eph = Ephemeris()
    conn = db.connect(args.db)

    shown = 0
    for row in db.all_eclipses(conn):
        year = int(row["peak_utc"][:4])
        if args.year_from and year < args.year_from:
            continue
        if args.year_to and year >= args.year_to:
            continue

        tl = local_timeline(eph, row, args.lat, args.lon)
        if not args.all and tl["verdict"] == "not visible":
            continue

        shown += 1
        note = _crossing_note(tl) if tl["verdict"] == "partially visible" else ""
        print(f"{row['peak_utc']}  {tl['kind']:10} {tl['verdict']:18}{note}".rstrip())

        if args.timeline:
            for r in tl["contacts"]:
                mark = "up" if r["up"] else "below horizon"
                print(f"      {r['label']:9} {r['time'].utc_strftime('%H:%M')} UTC   "
                      f"alt {r['altitude_deg']:6.1f}   {mark}")
            print()

    print(f"\n{shown} eclipse(s).")
    conn.close()


if __name__ == "__main__":
    main()