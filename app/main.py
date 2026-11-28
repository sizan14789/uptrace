from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app import db
from app.checker import check_site


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    # task = asyncio.create_task(engine())
    yield
    # task.cancel()
    await db.close()


app = FastAPI(lifespan=lifespan)


# monitor list
@app.get("/monitors")
async def monitors():
    rows = await db.pool.fetch("SELECT * FROM monitors")
    return [dict(r) for r in rows]


# single monitor info
@app.get("/monitors/{monitor_id}")
async def monitor_by_id(monitor_id: int):
    row = await db.pool.fetchrow("SELECT * FROM monitors WHERE id = $1", monitor_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return dict(row)


# all monitor latest status
@app.get("/status")
async def status():
    rows = await db.pool.fetch(
        "SELECT DISTINCT ON (monitor_id) monitor_id, status, status_code, checked_at FROM monitoring_results ORDER BY monitor_id, checked_at DESC"
    )
    return [dict(r) for r in rows]


# single monitor history
@app.get("/status/{monitor_id}")
async def status_per_monitor(monitor_id: int):
    rows = await db.pool.fetch(
        "SELECT monitor_id, status, status_code, checked_at FROM monitoring_results WHERE monitor_id = $1 ORDER BY checked_at DESC",
        monitor_id,
    )
    return [dict(r) for r in rows]


# dev ————————————————————————————
@app.get("/health")
async def health():
    return {"status": "ok"}


# for checking every site manually, no saving
@app.get("/check")
async def check():
    monitors = await db.pool.fetch("SELECT * FROM monitors WHERE status = 'ACTIVE'")
    results = []
    for m in monitors:
        up = await check_site(m["url"], m["timeout"])
        results.append({"id": m["id"], "name": m["name"], "up": "UP" if up else "DOWN"})
    return results
