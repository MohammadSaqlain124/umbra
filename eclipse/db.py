"""SQLite persistence: compute the catalogue once, read it forever."""

import os
import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS lunar_eclipses (
    id                 INTEGER PRIMARY KEY,
    peak_utc           TEXT    NOT NULL,   -- ISO 8601, greatest eclipse
    peak_jd_tt         REAL    NOT NULL,   -- Terrestrial Time JD, the exact anchor
    kind               TEXT    NOT NULL,   -- Penumbral | Partial | Total
    umbral_magnitude   REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_peak_jd ON lunar_eclipses(peak_jd_tt);
"""


def connect(db_path):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row   # rows behave like dicts: row["kind"]
    return conn


def init_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def insert_eclipses(conn, rows):
    conn.executemany(
        """
        INSERT INTO lunar_eclipses (peak_utc, peak_jd_tt, kind, umbral_magnitude)
        VALUES (:peak_utc, :peak_jd_tt, :kind, :umbral_magnitude)
        """,
        rows,
    )
    conn.commit()


def all_eclipses(conn):
    return conn.execute(
        "SELECT * FROM lunar_eclipses ORDER BY peak_jd_tt"
    ).fetchall()