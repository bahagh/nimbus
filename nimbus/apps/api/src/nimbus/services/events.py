from __future__ import annotations
from typing import List, Dict, Any
from uuid import uuid4, UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from nimbus.repositories.events import bulk_insert_events

def _to_dt(ts: Any) -> datetime:
    """Return a naive UTC datetime for DB (TIMESTAMP WITHOUT TIME ZONE)."""
    if isinstance(ts, datetime):
        dt = ts
    else:
        # Accept ISO8601 strings; handle trailing 'Z'
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            dt = datetime.now(timezone.utc)

    # Make it timezone-aware UTC
    if dt.tzinfo is None:
        dt_aware = dt.replace(tzinfo=timezone.utc)
    else:
        dt_aware = dt.astimezone(timezone.utc)

    # Return naive UTC for Postgres column without tz
    return dt_aware.replace(tzinfo=None)

async def ingest_events(session: AsyncSession, project_id: str, events: List[Dict[str, Any]]) -> int:
    """Validate/shape records, insert, and COMMIT."""
    records: List[Dict[str, Any]] = []
    # Convert project_id string to UUID
    project_uuid = UUID(project_id)
    
    for e in events:
        records.append({
            "id": e.get("id") or uuid4(),
            "project_id": project_uuid,
            "name": e["name"],
            "ts": _to_dt(e.get("ts") or datetime.now(timezone.utc)),
            "props": e.get("props", {}),
            "user_id": e.get("user_id"),
            "seq": e.get("seq"),
            "idempotency_key": e.get("idempotency_key"),
        })

    if not records:
        return 0

    inserted_count = await bulk_insert_events(session, records)
    await session.commit()  # ensure rows persist
    return inserted_count
