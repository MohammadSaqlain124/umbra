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