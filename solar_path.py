from eclipse.ephemeris import Ephemeris
from eclipse.solar import find_solar_eclipses
from eclipse.shadow import trace_path

eph = Ephemeris()
t0, t1 = eph.ts.utc(2024, 4, 1), eph.ts.utc(2024, 4, 15)
e = next(iter(find_solar_eclipses(eph, t0, t1)))

path = trace_path(eph, e["time"])
print(f"{e['kind']} eclipse of {e['time'].utc_strftime('%Y-%m-%d')} -- centerline")
if not path:
    print("  partial eclipse: no central path")
else:
    span = f"{path[0][0].utc_strftime('%H:%M')}-{path[-1][0].utc_strftime('%H:%M')} UTC"
    print(f"  {len(path)} points, {span}\n")
    for t, la, lo in path[::8]:
        ns = "N" if la >= 0 else "S"
        ew = "E" if lo >= 0 else "W"
        print(f"  {t.utc_strftime('%H:%M')}   {abs(la):5.1f}{ns}   {abs(lo):6.1f}{ew}")