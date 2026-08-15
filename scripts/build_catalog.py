"""Build the lunar eclipse catalogue. Run once; query forever."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eclipse.ephemeris import Ephemeris
from eclipse.pipeline import find_lunar_eclipses, to_records
from eclipse import db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2050)
    parser.add_argument("--db", default="data/eclipses.db")
    args = parser.parse_args()

    eph = Ephemeris()
    t0 = eph.ts.utc(args.start, 1, 1)
    t1 = eph.ts.utc(args.end, 1, 1)

    print(f"Finding lunar eclipses {args.start}-{args.end}...")
    rows = list(to_records(find_lunar_eclipses(eph, t0, t1)))
    print(f"  found {len(rows)} eclipses")

    conn = db.connect(args.db)
    db.init_schema(conn)
    conn.execute("DELETE FROM lunar_eclipses")   # clean rebuild
    db.insert_eclipses(conn, rows)
    conn.close()

    size_kb = os.path.getsize(args.db) // 1024
    print(f"Wrote {args.db} ({size_kb} KB)")


if __name__ == "__main__":
    main()