"""Contact times: the seven moments that mark an eclipse's progress."""

import numpy as np
from numpy import arcsin
from skyfield.searchlib import find_discrete

# Physical radii in km. These match Skyfield's own eclipse math, so our
# contact times stay consistent with the catalogue's classification.
EARTH_RADIUS = 6378.1366
SUN_RADIUS = 696340.0
MOON_RADIUS = 1737.1


def _shadow_geometry(eph, t):
    # At time t, return four angles (radians), all seen from Earth's centre:
    # how far the Moon sits from the shadow axis, plus the three radii that
    # define the Moon's disc and the two shadow cones. Written to accept an
    # array of times, because find_discrete passes many at once.
    seen = eph.earth.at(t)
    v_sun = seen.observe(eph.sun).position.km
    v_moon = seen.observe(eph.moon).position.km

    d_sun = np.linalg.norm(v_sun, axis=0)
    d_moon = np.linalg.norm(v_moon, axis=0)

    # Angle between the Moon and the anti-solar point (the shadow's axis).
    cos_sep = np.sum(-v_sun * v_moon, axis=0) / (d_sun * d_moon)
    separation = np.arccos(np.clip(cos_sep, -1.0, 1.0))

    pi_1 = 1.01 * EARTH_RADIUS / d_moon    # Danjon-enlarged Moon parallax
    pi_s = EARTH_RADIUS / d_sun
    s_s = SUN_RADIUS / d_sun

    penumbra_r = pi_1 + pi_s + s_s
    umbra_r = pi_1 + pi_s - s_s
    moon_r = arcsin(MOON_RADIUS / d_moon)
    return separation, moon_r, umbra_r, penumbra_r


def _crossing(eph, kind):
    # Build a boolean "is the Moon inside this region?" function for
    # find_discrete. step_days sets how finely the window is first scanned.
    def inside(t):
        sep, moon_r, umbra_r, penumbra_r = _shadow_geometry(eph, t)
        if kind == "penumbra":
            return sep < penumbra_r + moon_r
        if kind == "umbra":
            return sep < umbra_r + moon_r
        return sep < umbra_r - moon_r      # total
    inside.step_days = 0.01
    return inside


# Each shadow region, with the two contact labels that bracket it.
_REGIONS = [
    ("penumbra", "P1", "P4"),
    ("umbra", "U1", "U4"),
    ("total", "U2", "U3"),
]


def contact_times(eph, peak_jd_tt):
    # Search a 0.3-day window either side of greatest eclipse (wider than the
    # longest lunar eclipse). Contacts that never happen -- totality for a
    # partial eclipse, say -- simply don't appear, because there's no crossing.
    peak = eph.ts.tt_jd(peak_jd_tt)
    t0 = eph.ts.tt_jd(peak.tt - 0.3)
    t1 = eph.ts.tt_jd(peak.tt + 0.3)

    result = {"greatest": peak}
    for kind, begin, end in _REGIONS:
        times, _ = find_discrete(t0, t1, _crossing(eph, kind))
        if len(times) == 2:
            result[begin] = times[0]
            result[end] = times[1]
    return result