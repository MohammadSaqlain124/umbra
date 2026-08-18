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

def trace_path(eph, t_center, half_window_hours=3.0, step_minutes=2):
    # Step the shadow across Earth and record the centre at each moment the
    # umbra is actually on the surface. The result is the centreline -- the
    # curve drawn on every eclipse map. A partial eclipse yields an empty list.
    steps = int(half_window_hours * 60 / step_minutes)
    path = []
    for i in range(-steps, steps + 1):
        t = eph.ts.tt_jd(t_center.tt + (i * step_minutes) / 1440.0)
        pt = sub_shadow_point(eph, t)
        if pt is not None:
            path.append((t, pt[0], pt[1]))
    return path

def _bearing(lat1, lon1, lat2, lon2):
    la1, lo1, la2, lo2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlon = lo2 - lo1
    return np.arctan2(np.sin(dlon) * np.cos(la2),
                      np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(dlon))


def _offset(lat, lon, bearing_rad, dist_km):
    R = 6371.0
    la1, lo1 = np.radians(lat), np.radians(lon)
    d = dist_km / R
    la2 = np.arcsin(np.sin(la1) * np.cos(d) + np.cos(la1) * np.sin(d) * np.cos(bearing_rad))
    lo2 = lo1 + np.arctan2(np.sin(bearing_rad) * np.sin(d) * np.cos(la1),
                           np.cos(d) - np.sin(la1) * np.sin(la2))
    return float(np.degrees(la2)), float(np.degrees(lo2))


def path_limits(eph, t_center):
    # The centreline plus the two edges of the umbral band, each a list of
    # (lat, lon). Edges are the centreline offset left/right by half the local
    # path width, perpendicular to the direction of travel.
    path = trace_path(eph, t_center)
    center, north, south = [], [], []
    for i in range(len(path)):
        t, la, lo = path[i]
        if i + 1 < len(path):
            brg = _bearing(la, lo, path[i + 1][1], path[i + 1][2])
        else:
            brg = _bearing(path[i - 1][1], path[i - 1][2], la, lo)
        half = path_width_km(eph, t) / 2.0
        center.append((float(la), float(lo)))
        north.append(_offset(la, lo, brg - np.pi / 2, half))
        south.append(_offset(la, lo, brg + np.pi / 2, half))
    return center, north, south