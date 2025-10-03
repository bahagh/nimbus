from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from nimbus.repositories.metrics import fetch_metrics

async def get_event_count_series(session: AsyncSession, project_id: str, bucket: str = "1h", limit: int = 24) -> List[Dict]:
    return await fetch_metrics(session, project_id=project_id, bucket=bucket, limit=limit)
