from eclipse.ephemeris import Ephemeris
from eclipse.solar import find_solar_eclipses
from eclipse.observer import solar_circumstances

eph = Ephemeris()
t0, t1 = eph.ts.utc(2024, 4, 1), eph.ts.utc(2024, 4, 15)
e = next(iter(find_solar_eclipses(eph, t0, t1)))
tg = e["time"]
print(f"{e['kind']} solar eclipse of {tg.utc_strftime('%Y-%m-%d')} -- what each city sees:\n")

cities = [("Mazatlan, MX", 23.25, -106.41), ("Dallas, US", 32.78, -96.80),
          ("New York, US", 40.71, -74.01), ("London, UK", 51.51, -0.13),
          ("Aligarh, IN", 28.27, 79.17)]
for name, lat, lon in cities:
    c = solar_circumstances(eph, tg, lat, lon)
    line = f"{name:14} {c['kind']:13}"
    if c["kind"] in ("Total", "Annular", "Partial"):
        line += f"  mag {c['magnitude']:.2f}  Sun {c['sun_altitude_deg']:.0f} deg"
    if c.get("duration_s"):
        s = c["duration_s"]
        line += f"  duration {s // 60}m{s % 60:02d}s"
    print(line)