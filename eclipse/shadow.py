"""Where does the Moon's shadow fall on Earth?"""

import numpy as np
from skyfield.positionlib import Geocentric
from skyfield.units import Distance
from skyfield.api import wgs84

A = 6378.137   # WGS84 equatorial radius, km
B = 6356.752   # WGS84 polar radius, km


def _axis(eph, t):
    # The shadow axis as (a point on it, its direction): the Moon's position,
    # and the unit vector from the Sun through the Moon on toward Earth.
    e = eph.earth.at(t)
    r_sun = e.observe(eph.sun).apparent().position.km
    r_moon = e.observe(eph.moon).apparent().position.km
    axis = r_moon - r_sun
    axis = axis / np.linalg.norm(axis)
    return r_moon, axis


def sub_shadow_point(eph, t):
    # Intersect the shadow axis with Earth's ellipsoid; return the (lat, lon)
    # of the near-side hit -- the shadow's centre on the ground. Returns None
    # when the axis misses Earth (a partial eclipse has no central point).
    r_moon, axis = _axis(eph, t)

    # Squash the polar axis so the ellipsoid becomes a sphere of radius A,
    # solve the ray-sphere intersection there, then read the hit in real coords.
    squash = np.array([1.0, 1.0, A / B])
    m = r_moon * squash
    d = axis * squash
    qa = np.dot(d, d)
    qb = 2 * np.dot(m, d)
    qc = np.dot(m, m) - A * A
    disc = qb * qb - 4 * qa * qc
    if disc < 0:
        return None                        # axis misses Earth -> partial only

    s = (-qb - np.sqrt(disc)) / (2 * qa)    # near-side (day-side) root
    hit_km = r_moon + s * axis

    geocentric = Geocentric(Distance(km=hit_km).au, t=t)
    ground = wgs84.subpoint(geocentric)
    return ground.latitude.degrees, ground.longitude.degrees