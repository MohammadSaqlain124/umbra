import os
from skyfield.api import load, load_file


def _resolve_bsp_path():
    # Prefer an explicit kernel you point at; otherwise fall back to the
    # de421 that ships inside skyfield-data (only 1899-2053, fine for now).
    env = os.environ.get("UMBRA_EPHEMERIS")
    if env:
        return env
    from skyfield_data import get_skyfield_data_path
    return os.path.join(get_skyfield_data_path(), "de421.bsp")


class Ephemeris:
    def __init__(self, path=None):
        self.path = path or _resolve_bsp_path()
        self.ts = load.timescale()
        self.kernel = load_file(self.path)

        # Usable window = the intersection of every segment's span.
        segments = self.kernel.spk.segments
        self.start_jd = max(s.start_jd for s in segments)
        self.end_jd = min(s.end_jd for s in segments)

    def coverage(self):
        lo = self.ts.tt_jd(self.start_jd).utc_strftime("%Y-%m-%d")
        hi = self.ts.tt_jd(self.end_jd).utc_strftime("%Y-%m-%d")
        return lo, hi
    
    def clamp(self, start_year, end_year, margin_days=10.0):
        # Trim a requested [start_year, end_year] down to what the kernel
        # can actually cover, so a build never charges past the file's edge.
        req_lo = self.ts.utc(start_year, 1, 1)
        req_hi = self.ts.utc(end_year, 1, 1)

        # Pull the edges inward by a margin: the eclipse-finder walks a 5-day
        # grid and refines each peak with a parabola that can reach up to one
        # step beyond an endpoint. Landing right on the boundary re-triggers
        # the OutOfRange crash, so we stay 10 days clear.
        cov_lo = self.ts.tt_jd(self.start_jd + margin_days)
        cov_hi = self.ts.tt_jd(self.end_jd - margin_days)

        t_start = req_lo if req_lo.tt >= cov_lo.tt else cov_lo
        t_end = req_hi if req_hi.tt <= cov_hi.tt else cov_hi
        was_clamped = (t_start.tt != req_lo.tt) or (t_end.tt != req_hi.tt)
        return t_start, t_end, was_clamped
    
    @property
    def earth(self):
        return self.kernel["earth"]

    @property
    def moon(self):
        return self.kernel["moon"]
    
    @property
    def sun(self):
        return self.kernel["sun"]