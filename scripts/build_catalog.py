import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eclipse.ephemeris import Ephemeris
from eclipse.pipeline import find_lunar_eclipses, to_records
from eclipse.solar import find_solar_eclipses, to_solar_records
from eclipse import db


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, default=2000)
    p.add_argument("--end", type=int, default=2050)
    p.add_argument("--db", default="data/eclipses.db")
    a = p.parse_args()

    eph = Ephemeris()
    t0, t1, _ = eph.clamp(a.start, a.end)

    conn = db.connect(a.db)
    db.init_schema(conn)
    db.init_solar_schema(conn)

    lunar = list(to_records(find_lunar_eclipses(eph, t0, t1)))
    conn.execute("DELETE FROM lunar_eclipses")
    db.insert_eclipses(conn, lunar)
    print(f"lunar:  {len(lunar)} eclipses")

    solar = list(to_solar_records(eph, find_solar_eclipses(eph, t0, t1)))
    conn.execute("DELETE FROM solar_eclipses")
    db.insert_solar_eclipses(conn, solar)
    print(f"solar:  {len(solar)} eclipses")

    conn.close()


if __name__ == "__main__":
    main()