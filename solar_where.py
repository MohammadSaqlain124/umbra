from eclipse.ephemeris import Ephemeris
from eclipse.solar import find_solar_eclipses
from eclipse.shadow import sub_shadow_point, path_width_km

eph = Ephemeris()
t0, t1 = eph.ts.utc(2023, 1, 1), eph.ts.utc(2027, 1, 1)

print(f"{'date':12} {'type':8} {'greatest-eclipse point':22} width")
print("-" * 56)
for e in find_solar_eclipses(eph, t0, t1):
    pt = sub_shadow_point(eph, e["time"])
    date = e["time"].utc_strftime("%Y-%m-%d")
    if pt is None:
        print(f"{date}  {e['kind']:8} no central point (partial)")
        continue
    lat, lon = pt
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    where = f"{abs(lat):5.2f}{ns}  {abs(lon):6.2f}{ew}"
    w = path_width_km(eph, e["time"])
    print(f"{date}  {e['kind']:8} {where:22} {w:4.0f} km")