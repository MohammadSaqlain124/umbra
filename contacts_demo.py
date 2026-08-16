from eclipse.ephemeris import Ephemeris
from eclipse.contacts import contact_times
from eclipse import db

eph = Ephemeris()
conn = db.connect("data/eclipses.db")

# Pull the deep total of 2025-09-07 out of your catalogue.
row = next(r for r in db.all_eclipses(conn) if r["peak_utc"].startswith("2025-09-07"))
print(f"{row['kind']} lunar eclipse of {row['peak_utc'][:10]}\n")

contacts = contact_times(eph, row["peak_jd_tt"])
for label, t in sorted(contacts.items(), key=lambda kv: kv[1].tt):
    print(f"  {label:9} {t.utc_strftime('%H:%M:%S')} UTC")

conn.close()