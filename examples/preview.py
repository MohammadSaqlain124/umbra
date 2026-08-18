from eclipse.ephemeris import Ephemeris
from eclipse.pipeline import find_lunar_eclipses

eph = Ephemeris()
t0 = eph.ts.utc(2023, 1, 1)
t1 = eph.ts.utc(2026, 1, 1)

print(f"{'date (UTC)':17} {'ours':10} {'skyfield':10} {'umbral mag':>10}  check")
print("-" * 60)
for e in find_lunar_eclipses(eph, t0, t1):
    when = e["time"].utc_strftime("%Y-%m-%d %H:%M")
    check = "OK" if e["kind"] == e["skyfield_kind"] else "MISMATCH"
    print(f"{when:17} {e['kind']:10} {e['skyfield_kind']:10} "
          f"{e['umbral_magnitude']:10.3f}  {check}")