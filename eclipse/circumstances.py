"""Local circumstances: was a given eclipse above your horizon?"""

from skyfield.api import wgs84

_COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def _compass(az_degrees):
    return _COMPASS[int((az_degrees % 360) / 22.5 + 0.5) % 16]


def local_circumstances(eph, eclipse_row, latitude, longitude):
    # The eclipse peak is one exact instant (stored as a TT Julian Date).
    # We ask: from this spot on Earth, where was the Moon at that instant?
    t = eph.ts.tt_jd(eclipse_row["peak_jd_tt"])

    site = wgs84.latlon(latitude, longitude)
    observer = eph.earth + site                      # you, standing on Earth
    app = observer.at(t).observe(eph.moon).apparent()
    alt, az, _ = app.altaz()                         # altitude & compass bearing

    return {
        "peak_utc": eclipse_row["peak_utc"],
        "kind": eclipse_row["kind"],
        "umbral_magnitude": round(eclipse_row["umbral_magnitude"], 3),
        "moon_altitude_deg": round(alt.degrees, 1),
        "moon_azimuth_deg": round(az.degrees, 1),
        "moon_direction": _compass(az.degrees),
        "visible": alt.degrees > 0,                  # above the horizon = you saw it
    }