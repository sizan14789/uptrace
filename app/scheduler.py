from app import db
import asyncio
from app.checker import check_site

last_checked_at = {}


async def tick():
    now = asyncio.get_event_loop().time()  # time since loop started
    monitors = await db.pool.fetch("SELECT * FROM monitors WHERE status = 'ACTIVE'")
    results = []

    for m in monitors:
        if (
            m["id"] in last_checked_at
            and now - last_checked_at[m["id"]] < m["interval"]
        ):
            continue

        last_checked_at[m["id"]] = now
        response = await check_site(m["url"], m["timeout"])

        await db.pool.execute(
            "INSERT INTO monitoring_results (monitor_id, status, status_code, error) VALUES ($1, $2, $3, $4)",
            m["id"],
            "UP" if response["up"] else "DOWN",
            response["status_code"],
            response["error"],
        )


async def engine():
    while True:
        await tick()
        await asyncio.sleep(60)
