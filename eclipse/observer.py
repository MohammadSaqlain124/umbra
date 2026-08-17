"""What does an observer at a given location see during a solar eclipse?"""

import numpy as np
from skyfield.api import wgs84
from skyfield.searchlib import find_minima, find_discrete

R_SUN = 696000.0
R_MOON = 1737.4


def _angles(site, sun, moon, t):
    # Topocentric view: Sun and Moon as the observer sees them at time t.
    # Returns their separation, each disc's angular radius (deg), Sun altitude.
    a = site.at(t)
    s = a.observe(sun).apparent()
    m = a.observe(moon).apparent()
    sep = s.separation_from(m).degrees
    sun_r = np.degrees(np.arcsin(R_SUN / s.distance().km))
    moon_r = np.degrees(np.arcsin(R_MOON / m.distance().km))
    return sep, sun_r, moon_r, s.altaz()[0].degrees


def solar_circumstances(eph, t_center, latitude, longitude):
    site = eph.earth + wgs84.latlon(latitude, longitude)
    sun, moon = eph.sun, eph.moon

    # Moment of maximum eclipse here = when the two discs are closest.
    def sep_only(t):
        a = site.at(t)
        return a.observe(sun).apparent().separation_from(a.observe(moon).apparent()).degrees
    sep_only.step_days = 0.002

    window = 0.11   # ~2.6 hours either side of global greatest eclipse
    tmin, _ = find_minima(eph.ts.tt_jd(t_center.tt - window),
                          eph.ts.tt_jd(t_center.tt + window), sep_only)
    if len(tmin) == 0:
        return {"kind": "none"}
    tm = tmin[0]

    sep, sun_r, moon_r, sun_alt = _angles(site, sun, moon, tm)
    magnitude = (sun_r + moon_r - sep) / (2 * sun_r)

    if sun_alt < 0:
        kind = "below horizon"
    elif sep < moon_r - sun_r:
        kind = "Total"
    elif sep < sun_r - moon_r:
        kind = "Annular"
    elif magnitude > 0:
        kind = "Partial"
    else:
        kind = "none"

    result = {"max_time": tm, "sun_altitude_deg": round(sun_alt, 1),
              "kind": kind, "magnitude": round(max(magnitude, 0.0), 3),
              "duration_s": None}

    # How long does totality / annularity last from here?
    if kind in ("Total", "Annular"):
        def central(t):
            sep, sun_r, moon_r, _ = _angles(site, sun, moon, t)
            return sep < abs(moon_r - sun_r)
        central.step_days = 0.0005
        tc, _ = find_discrete(eph.ts.tt_jd(tm.tt - 0.02),
                              eph.ts.tt_jd(tm.tt + 0.02), central)
        if len(tc) == 2:
            result["duration_s"] = round((tc[1].tt - tc[0].tt) * 86400)

    return result