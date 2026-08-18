"""umbra web API and site."""

import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from eclipse.ephemeris import Ephemeris
from eclipse.query import find_events
from eclipse import db

app = FastAPI(title="umbra", description="High-precision eclipse prediction")

EPH = Ephemeris()
DB_PATH = os.environ.get("UMBRA_DB", "data/eclipses.db")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/eclipses")
def eclipses(lat: float, lon: float, year_from: int | None = None, year_to: int | None = None):
    # Cap the span: solar circumstances are computed live, so an unbounded
    # range would be slow on a small instance.
    if year_from is not None and year_to is not None and year_to - year_from > 20:
        year_to = year_from + 20
    conn = db.connect(DB_PATH)
    events = find_events(EPH, conn, lat, lon, year_from, year_to)
    conn.close()
    return {"lat": lat, "lon": lon, "count": len(events), "eclipses": events}


@app.get("/api/path")
def path(jd: float):
    from eclipse.shadow import path_limits
    center, north, south = path_limits(EPH, EPH.ts.tt_jd(jd))
    return {"center": center, "north": north, "south": south}


@app.get("/")
def index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")