from typing import List
import datetime as dt
from sqlalchemy.ext.asyncio import AsyncSession
from nimbus.repositories.events import bulk_insert_events

def _to_record(project_id: str, e: dict) -> dict:
    ts = e["ts"]
    if isinstance(ts, dt.datetime) and ts.tzinfo is not None:
        ts = ts.astimezone(dt.timezone.utc).replace(tzinfo=None)
    return {
        "project_id": project_id,
        "name": e["name"],
        "ts": ts,
        "props": e.get("props") or {},
        "user_id": e.get("user_id"),
        "seq": e.get("seq"),
    }

async def ingest_events(session: AsyncSession, project_id: str, incoming_events: List[dict]) -> int:
    records = [_to_record(project_id, e) for e in incoming_events]
    await bulk_insert_events(session, records)
    return len(records)
def _event_to_out(e) -> dict:
    return {
        "id": str(e.id),
        "project_id": str(e.project_id),
        "name": e.name,
        "ts": e.ts.isoformat(),
        "user_id": e.user_id,
        "seq": e.seq,
        "props": e.props or {},
    }