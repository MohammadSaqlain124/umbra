"""Find lunar eclipses and classify how deep each one is."""

from skyfield import eclipselib


def classify(separation, moon_r, umbra_r, penumbra_r):
    # Every argument is an angle in radians, seen from Earth's centre:
    #   separation  - how far the Moon's centre sits from the shadow's axis
    #   moon_r      - the Moon's own angular radius
    #   umbra_r     - radius of the dark inner shadow at the Moon's distance
    #   penumbra_r  - radius of the faint outer shadow
    #
    # Read deepest-first:
    if separation < umbra_r - moon_r:
        return "Total"        # the whole Moon fits inside the dark core
    if separation < umbra_r + moon_r:
        return "Partial"      # the Moon's edge dips into the core
    if separation < penumbra_r + moon_r:
        return "Penumbral"    # the Moon only grazes the faint outer shadow
    return "None"             # a clean miss - not an eclipse


def find_lunar_eclipses(eph, t0, t1):
    times, codes, details = eclipselib.lunar_eclipses(t0, t1, eph.kernel)

    separation = details["closest_approach_radians"]
    moon_r = details["moon_radius_radians"]
    umbra_r = details["umbra_radius_radians"]
    penumbra_r = details["penumbra_radius_radians"]
    umbral_mag = details["umbral_magnitude"]

    for i in range(len(times)):
        yield {
            "time": times[i],
            "kind": classify(separation[i], moon_r[i], umbra_r[i], penumbra_r[i]),
            "skyfield_kind": eclipselib.LUNAR_ECLIPSES[codes[i]],
            "umbral_magnitude": float(umbral_mag[i]),
        }

def to_records(eclipses):
    """Turn finder output into flat rows ready for the database."""
    for e in eclipses:
        t = e["time"]
        yield {
            "peak_utc": t.utc_strftime("%Y-%m-%dT%H:%M:%SZ"),
            "peak_jd_tt": float(t.tt),
            "kind": e["kind"],
            "umbral_magnitude": e["umbral_magnitude"],
        }