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
    conn = db.connect(DB_PATH)
    events = find_events(EPH, conn, lat, lon, year_from, year_to)
    conn.close()
    return {"lat": lat, "lon": lon, "count": len(events), "eclipses": events}


@app.get("/")
def index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")