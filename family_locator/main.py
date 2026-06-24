from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import time
from pathlib import Path
from contextlib import asynccontextmanager

DB_PATH = Path(__file__).parent / "locations.db"
DASHBOARD_HTML = Path(__file__).parent / "templates" / "dashboard.html"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id   TEXT NOT NULL,
            latitude    REAL NOT NULL,
            longitude   REAL NOT NULL,
            timestamp   INTEGER NOT NULL,
            battery_percentage INTEGER NOT NULL,
            device_name TEXT NOT NULL,
            received_at INTEGER NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_device_ts ON locations(device_id, timestamp DESC)")
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Family Locator Dashboard", lifespan=lifespan)


# ── Data model matching the Android app's LocationRequest ──────────────────
class LocationUpdate(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    timestamp: int          # Unix seconds
    battery_percentage: int
    device_name: str


# ── API: receive location from Android ────────────────────────────────────
@app.post("/location/update", status_code=200)
def receive_location(update: LocationUpdate):
    conn = get_db()
    conn.execute(
        """INSERT INTO locations
           (device_id, latitude, longitude, timestamp, battery_percentage, device_name, received_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            update.device_id,
            update.latitude,
            update.longitude,
            update.timestamp,
            update.battery_percentage,
            update.device_name,
            int(time.time()),
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "success"}


# ── API: latest position for every device ─────────────────────────────────
@app.get("/api/devices")
def get_devices():
    conn = get_db()
    rows = conn.execute("""
        SELECT l.*
        FROM locations l
        INNER JOIN (
            SELECT device_id, MAX(timestamp) AS max_ts
            FROM locations
            GROUP BY device_id
        ) latest ON l.device_id = latest.device_id AND l.timestamp = latest.max_ts
        ORDER BY l.received_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── API: location history for one device (last 50 points) ─────────────────
@app.get("/api/devices/{device_id}/history")
def get_history(device_id: str, limit: int = 50):
    conn = get_db()
    rows = conn.execute(
        """SELECT * FROM locations WHERE device_id = ?
           ORDER BY timestamp DESC LIMIT ?""",
        (device_id, limit),
    ).fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Device not found")
    return [dict(r) for r in rows]


# ── API: all history (last 200 rows across all devices) ───────────────────
@app.get("/api/history")
def get_all_history(limit: int = 200):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM locations ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Dashboard HTML ─────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=DASHBOARD_HTML.read_text(encoding="utf-8"))
