"""Draw a solar eclipse's band of totality on an interactive map."""

import folium
from eclipse.ephemeris import Ephemeris
from eclipse.solar import find_solar_eclipses
from eclipse.shadow import path_limits

eph = Ephemeris()
t0, t1 = eph.ts.utc(2024, 4, 1), eph.ts.utc(2024, 4, 15)
e = next(iter(find_solar_eclipses(eph, t0, t1)))

center, north, south = path_limits(eph, e["time"])
mid = center[len(center) // 2]

m = folium.Map(location=mid, zoom_start=3, tiles="CartoDB positron")
folium.Polygon(north + south[::-1], color=None, fill=True,
               fill_color="#b00020", fill_opacity=0.25,
               tooltip=f"{e['kind']} eclipse {e['time'].utc_strftime('%Y-%m-%d')} -- band of totality").add_to(m)
folium.PolyLine(center, color="#b00020", weight=2, opacity=0.9).add_to(m)
folium.Marker(center[0], tooltip="Landfall (sunrise limb)", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(mid, tooltip="Greatest eclipse", icon=folium.Icon(color="red")).add_to(m)
folium.Marker(center[-1], tooltip="Departs (sunset limb)", icon=folium.Icon(color="blue")).add_to(m)

out = f"eclipse_{e['time'].utc_strftime('%Y-%m-%d')}.html"
m.save(out)
print(f"wrote {out}: {len(center)} centerline points, band polygon {len(north)+len(south)} vertices")