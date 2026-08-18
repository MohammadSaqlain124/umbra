"""umbra web API."""

import os
from fastapi import FastAPI

from eclipse.ephemeris import Ephemeris
from eclipse.query import find_events
from eclipse import db

app = FastAPI(title="umbra", description="High-precision eclipse prediction")

EPH = Ephemeris()                                  # load ephemeris once at startup
DB_PATH = os.environ.get("UMBRA_DB", "data/eclipses.db")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/eclipses")
def eclipses(lat: float, lon: float, year_from: int | None = None, year_to: int | None = None):
    conn = db.connect(DB_PATH)
    events = find_events(EPH, conn, lat, lon, year_from, year_to)
    conn.close()
    return {"lat": lat, "lon": lon, "count": len(events), "eclipses": events}