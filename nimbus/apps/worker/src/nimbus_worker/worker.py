import asyncio, json
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from .config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

async def rollup_last_minute():
    async with SessionLocal() as s:
        rows = (await s.execute(text("""
            SELECT project_id, date_trunc('minute', ts) AS bucket, count(*)::int AS value
            FROM events WHERE ts > now() - interval '2 minutes'
            GROUP BY 1,2
        """))).all()
    for r in rows:
        payload = json.dumps({"series": [{"ts": r.bucket.isoformat(), "value": r.value}]})
        await redis.publish(f"metrics:{r.project_id}", payload)

async def scheduler():
    while True:
        await rollup_last_minute()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(scheduler())
