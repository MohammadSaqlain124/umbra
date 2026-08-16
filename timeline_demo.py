from eclipse.ephemeris import Ephemeris
from eclipse.circumstances import local_timeline
from eclipse import db

LAT, LON = 28.27, 79.17
eph = Ephemeris()
conn = db.connect("data/eclipses.db")

row = next(r for r in db.all_eclipses(conn) if r["peak_utc"].startswith("2026-03-03"))
tl = local_timeline(eph, row, LAT, LON)

print(f"{tl['kind']} lunar eclipse of {row['peak_utc'][:10]}  ->  {tl['verdict']}\n")
for r in tl["contacts"]:
    mark = "up" if r["up"] else "below horizon"
    print(f"  {r['label']:9} {r['time'].utc_strftime('%H:%M')} UTC   "
          f"alt {r['altitude_deg']:6.1f}   {mark}")
for c in tl["crossings"]:
    verb = "Moon rises" if c["rising"] else "Moon sets"
    print(f"\n  {verb} mid-eclipse at {c['time'].utc_strftime('%H:%M')} UTC")

conn.close()