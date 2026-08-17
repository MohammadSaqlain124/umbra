"""Find solar eclipses and classify each as total, annular, hybrid, or partial."""

import numpy as np
from skyfield.searchlib import find_minima

EARTH_RADIUS = 6378.137   # equatorial, km
SUN_RADIUS = 696000.0
MOON_RADIUS = 1737.4

CENTRAL_LIMIT = 0.9972    # gamma below this: shadow axis strikes Earth
PARTIAL_LIMIT = 1.55      # gamma beyond this: penumbra misses Earth entirely


def _separation(eph):
    # Geocentric angular gap between Sun and Moon. Its *minima* are the New
    # Moons -- the only moments a solar eclipse can occur. (Lunar used maxima
    # of the Sun-Moon angle to find Full Moons; this is the mirror image.)
    def f(t):
        e = eph.earth.at(t)
        sun = e.observe(eph.sun).apparent()
        moon = e.observe(eph.moon).apparent()
        return sun.separation_from(moon).degrees
    f.step_days = 5.0
    return f


def _shadow_axis_geometry(eph, t):
    # gamma: distance of the shadow axis from Earth's centre, in Earth radii.
    # size_ratio: Moon's apparent size / Sun's, seen from under the shadow.
    e = eph.earth.at(t)
    r_sun = e.observe(eph.sun).apparent().position.km
    r_moon = e.observe(eph.moon).apparent().position.km

    axis = r_moon - r_sun
    axis = axis / np.linalg.norm(axis)             # Sun -> Moon -> Earth
    perp = r_moon - np.dot(r_moon, axis) * axis    # centre-to-axis vector
    gamma = np.linalg.norm(perp) / EARTH_RADIUS

    d_moon = np.linalg.norm(r_moon)
    d_sun = np.linalg.norm(r_sun)
    moon_ang = np.arcsin(MOON_RADIUS / (d_moon - EARTH_RADIUS))  # topocentric
    sun_ang = np.arcsin(SUN_RADIUS / d_sun)
    return gamma, moon_ang / sun_ang


def _classify(gamma, size_ratio):
    if gamma >= CENTRAL_LIMIT:
        return "Partial"
    if size_ratio < 1.0:
        return "Annular"
    if size_ratio < 1.02:
        return "Hybrid"     # Moon barely wins; Earth's curve flips it annular
    return "Total"          #   at the path ends. Confirmed rigorously in 2.2.


def find_solar_eclipses(eph, t0, t1):
    conjunction = _separation(eph)
    times, _ = find_minima(t0, t1, conjunction)
    for t in times:
        gamma, size_ratio = _shadow_axis_geometry(eph, t)
        if gamma >= PARTIAL_LIMIT:
            continue                    # whole shadow misses Earth
        yield {"time": t, "gamma": round(float(gamma), 3),
               "kind": _classify(gamma, size_ratio)}