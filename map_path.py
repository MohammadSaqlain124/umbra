"""Draw a solar eclipse's path of totality on an interactive map."""

import folium
from eclipse.ephemeris import Ephemeris
from eclipse.solar import find_solar_eclipses
from eclipse.shadow import trace_path

eph = Ephemeris()
t0, t1 = eph.ts.utc(2024, 4, 1), eph.ts.utc(2024, 4, 15)
e = next(iter(find_solar_eclipses(eph, t0, t1)))

path = trace_path(eph, e["time"])
coords = [(float(la), float(lo)) for _, la, lo in path]   # folium wants (lat, lon)
mid = coords[len(coords) // 2]

m = folium.Map(location=mid, zoom_start=3, tiles="CartoDB positron")
folium.PolyLine(coords, color="#b00020", weight=3, opacity=0.85,
                tooltip=f"{e['kind']} eclipse {e['time'].utc_strftime('%Y-%m-%d')}").add_to(m)
folium.Marker(coords[0], tooltip="Umbra makes landfall (sunrise limb)",
              icon=folium.Icon(color="green")).add_to(m)
folium.Marker(mid, tooltip="Greatest eclipse",
              icon=folium.Icon(color="red")).add_to(m)
folium.Marker(coords[-1], tooltip="Umbra departs (sunset limb)",
              icon=folium.Icon(color="blue")).add_to(m)

out = f"eclipse_{e['time'].utc_strftime('%Y-%m-%d')}.html"
m.save(out)
print(f"wrote {out} -- open it in your browser")