from typing import List, Dict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_SQLITE_Q = """
SELECT
  strftime('%Y-%m-%dT%H:00:00Z', ts) as ts,
  COUNT(*) as value
FROM events
WHERE project_id = :project_id
GROUP BY 1
ORDER BY 1 DESC
LIMIT :limit
"""

_PG_Q = """
SELECT to_char(date_trunc(:bucket, ts), 'YYYY-MM-DD"T"HH24:00:00"Z"') AS ts,
       COUNT(*)::int AS value
FROM events
WHERE project_id = :project_id
GROUP BY 1
ORDER BY 1 DESC
LIMIT :limit
"""

async def fetch_metrics(session: AsyncSession, project_id: str, bucket: str = "1h", limit: int = 24) -> List[Dict]:
    if session.bind and session.bind.dialect.name == "postgresql":
        rows = (await session.execute(text(_PG_Q), {"project_id": project_id, "bucket": "hour", "limit": limit})).mappings().all()
    else:
        rows = (await session.execute(text(_SQLITE_Q), {"project_id": project_id, "limit": limit})).mappings().all()
    return list(reversed([dict(r) for r in rows]))
