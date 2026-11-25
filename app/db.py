from asyncpg import Pool, create_pool
from app.config import settings

pool: Pool | None = None

async def connect():
    global pool
    pool = await create_pool(settings.database_url, max_size=10)

async def close():
    await pool.close()