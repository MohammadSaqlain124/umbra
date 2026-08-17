"""Where does the Moon's shadow fall on Earth, and how wide is it?"""

import numpy as np
from skyfield.positionlib import Geocentric
from skyfield.units import Distance
from skyfield.api import wgs84

A = 6378.137    # WGS84 equatorial radius, km
B = 6356.752    # WGS84 polar radius, km
R_SUN = 696000.0
R_MOON = 1737.4


def _bodies(eph, t):
    e = eph.earth.at(t)
    r_sun = e.observe(eph.sun).apparent().position.km
    r_moon = e.observe(eph.moon).apparent().position.km
    return r_sun, r_moon


def _ground_hit(r_sun, r_moon):
    # Intersect the shadow axis with Earth's ellipsoid. Returns (hit_km, s,
    # axis): the near-side ground point, the Moon->ground distance, and the
    # axis direction. Returns None if the axis misses Earth (partial eclipse).
    axis = r_moon - r_sun
    axis = axis / np.linalg.norm(axis)
    squash = np.array([1.0, 1.0, A / B])
    m = r_moon * squash
    d = axis * squash
    qa = np.dot(d, d)
    qb = 2 * np.dot(m, d)
    qc = np.dot(m, m) - A * A
    disc = qb * qb - 4 * qa * qc
    if disc < 0:
        return None
    s = (-qb - np.sqrt(disc)) / (2 * qa)
    return r_moon + s * axis, s, axis


def sub_shadow_point(eph, t):
    r_sun, r_moon = _bodies(eph, t)
    hit = _ground_hit(r_sun, r_moon)
    if hit is None:
        return None
    hit_km, _, _ = hit
    ground = wgs84.subpoint(Geocentric(Distance(km=hit_km).au, t=t))
    return ground.latitude.degrees, ground.longitude.degrees


def path_width_km(eph, t):
    r_sun, r_moon = _bodies(eph, t)
    hit = _ground_hit(r_sun, r_moon)
    if hit is None:
        return None
    hit_km, s, axis = hit

    # Umbral cone: half-angle f2, apex a distance L2 beyond the Moon.
    D = np.linalg.norm(r_sun - r_moon)
    sin_f2 = (R_SUN - R_MOON) / D
    tan_f2 = sin_f2 / np.sqrt(1 - sin_f2 * sin_f2)
    L2 = R_MOON / sin_f2

    # Umbra (or antumbra) radius where it meets the ground, across the axis.
    rho = abs(L2 - s) * tan_f2

    # A low Sun stretches the footprint: divide by the cosine of the axis
    # against the local (ellipsoid) vertical.
    normal = np.array([hit_km[0] / A**2, hit_km[1] / A**2, hit_km[2] / B**2])
    normal = normal / np.linalg.norm(normal)
    cos_tilt = abs(np.dot(axis, normal))

    return 2 * rho / cos_tilt