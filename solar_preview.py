from eclipse.ephemeris import Ephemeris
from eclipse.solar import find_solar_eclipses

eph = Ephemeris()
t0 = eph.ts.utc(2023, 1, 1)
t1 = eph.ts.utc(2027, 1, 1)

print(f"{'date (UTC)':13} {'gamma':>7}  {'type':8}")
print("-" * 32)
for e in find_solar_eclipses(eph, t0, t1):
    print(f"{e['time'].utc_strftime('%Y-%m-%d')}   {e['gamma']:>6.3f}  {e['kind']}")