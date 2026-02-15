"""Windows VM uptime monitor.

Periodically checks:
  1. Tailscale ping to the Windows VM (is the machine running?)
  2. HTTP probe to localhost:9006 (is the noVNC SSH tunnel up?)

Stores results in SQLite for historical trends and exposes a
FastAPI API for the admin dashboard to consume.
"""

import asyncio
import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Configuration (all overridable via env vars)
# ---------------------------------------------------------------------------
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))  # seconds
TUNNEL_HOST = os.getenv("TUNNEL_HOST", "127.0.0.1")
TUNNEL_PORT = int(os.getenv("TUNNEL_PORT", "9006"))
VM_TAILSCALE_IP = os.getenv("VM_TAILSCALE_IP", "")  # e.g. 100.x.y.z
DB_PATH = os.getenv("DB_PATH", "/app/data/vm-monitor.db")
PROBE_TIMEOUT = int(os.getenv("PROBE_TIMEOUT", "5"))  # seconds

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at TEXT    NOT NULL,
                vm_up      INTEGER NOT NULL,
                tunnel_up  INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_checks_time
            ON checks(checked_at)
        """)


def store_check(vm_up: bool, tunnel_up: bool):
    now = datetime.now(timezone.utc).isoformat()
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO checks (checked_at, vm_up, tunnel_up) VALUES (?, ?, ?)",
            (now, int(vm_up), int(tunnel_up)),
        )


def get_latest() -> dict | None:
    with _get_db() as conn:
        row = conn.execute(
            "SELECT checked_at, vm_up, tunnel_up FROM checks ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return {"checked_at": row["checked_at"], "vm_up": bool(row["vm_up"]), "tunnel_up": bool(row["tunnel_up"])}


def get_history(hours: int = 24) -> list[dict]:
    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT checked_at, vm_up, tunnel_up FROM checks WHERE checked_at >= ? ORDER BY checked_at",
            (cutoff_iso,),
        ).fetchall()
    return [{"checked_at": r["checked_at"], "vm_up": bool(r["vm_up"]), "tunnel_up": bool(r["tunnel_up"])} for r in rows]


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------

async def check_tunnel() -> bool:
    """HTTP probe to the noVNC tunnel endpoint."""
    url = f"http://{TUNNEL_HOST}:{TUNNEL_PORT}/"
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:
            resp = await client.get(url)
            return resp.status_code < 500
    except Exception:
        return False


async def check_vm() -> bool:
    """Tailscale ping to the Windows VM.

    Falls back to True if no VM_TAILSCALE_IP is configured (so the
    tunnel check alone drives the status).
    """
    if not VM_TAILSCALE_IP:
        return True  # no IP configured — skip this check

    try:
        # asyncio.create_subprocess_exec is safe — no shell interpolation,
        # arguments are passed as a list (not through a shell).
        proc = await asyncio.create_subprocess_exec(
            "tailscale", "ping", "--timeout=3s", "-c", "1", VM_TAILSCALE_IP,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, _ = await asyncio.wait_for(proc.communicate(), timeout=PROBE_TIMEOUT)
        return proc.returncode == 0
    except Exception:
        # tailscale not installed or timed out — fall back to ICMP ping
        try:
            proc = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "3", VM_TAILSCALE_IP,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, _ = await asyncio.wait_for(proc.communicate(), timeout=PROBE_TIMEOUT)
            return proc.returncode == 0
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Background polling loop
# ---------------------------------------------------------------------------

_poll_task: asyncio.Task | None = None


async def poll_loop():
    while True:
        vm_up, tunnel_up = await asyncio.gather(check_vm(), check_tunnel())
        store_check(vm_up, tunnel_up)
        await asyncio.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    global _poll_task
    _poll_task = asyncio.create_task(poll_loop())
    yield
    if _poll_task:
        _poll_task.cancel()


app = FastAPI(title="VM Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/status")
def status():
    latest = get_latest()
    if latest is None:
        return {"vm_up": None, "tunnel_up": None, "checked_at": None}
    return latest


@app.get("/history")
def history(hours: int = 24):
    return get_history(hours)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "vm-monitor"}
