from eclipse.ephemeris import Ephemeris
from eclipse.circumstances import local_circumstances
from eclipse import db

LAT, LON = 28.27, 79.17          
YEAR_FROM, YEAR_TO = 2023, 2027  

eph = Ephemeris()
conn = db.connect("data/eclipses.db")

print(f"Lunar eclipses from lat {LAT}, lon {LON}  ({YEAR_FROM}-{YEAR_TO}):\n")
for row in db.all_eclipses(conn):
    year = int(row["peak_utc"][:4])
    if not (YEAR_FROM <= year < YEAR_TO):
        continue
    c = local_circumstances(eph, row, LAT, LON)
    tag = "visible" if c["visible"] else "(below horizon)"
    print(f"{c['peak_utc']}  {c['kind']:10} mag {c['umbral_magnitude']:6.2f}  "
          f"alt {c['moon_altitude_deg']:>6}°  {c['moon_direction']:>3}  {tag}")

conn.close()