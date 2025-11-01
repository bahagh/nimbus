from __future__ import annotations
from sqlalchemy.dialects.postgresql import insert as pg_insert
import uuid as _uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from nimbus.models.event import Event

async def bulk_insert_events(session: AsyncSession, records: List[Dict[str, Any]]) -> int:
    """
    Insert many events. Skips duplicates if idempotency_key is provided (idempotent).
    """
    if not records:
        return 0

    # Ensure each record has a UUID id
    for r in records:
        r.setdefault("id", _uuid.uuid4())
    
    # Check if any record has idempotency_key - if so, use ON CONFLICT
    has_idempotency_key = any(r.get("idempotency_key") is not None for r in records)
    
    stmt = pg_insert(Event).values(records)
    
    if has_idempotency_key:
        # Use ON CONFLICT only when idempotency_key is provided
        # Note: The constraint uses COALESCE(user_id, '') and WHERE idempotency_key IS NOT NULL
        stmt = stmt.on_conflict_do_nothing(
            index_elements=[Event.project_id, Event.name, Event.ts, Event.user_id, Event.idempotency_key]
        )
    
    stmt = stmt.returning(Event.id)

    res = await session.execute(stmt)
    inserted = len(res.fetchall())
    # Remove duplicate commit - let the service handle it
    return inserted

async def list_events_offset(
    session: AsyncSession,
    project_id: str,
    limit: int,
    offset: int,
    name: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    props_contains: Optional[Dict[str, Any]] = None,
):
    q = select(Event).where(Event.project_id == _uuid.UUID(project_id))
    if name:
        q = q.where(Event.name.in_(name))
    if user_id:
        q = q.where(Event.user_id == user_id)
    if since:
        q = q.where(Event.ts >= since)
    if until:
        q = q.where(Event.ts < until)
    if props_contains:
        from sqlalchemy import func
        q = q.where(func.jsonb_contains(Event.props, props_contains))  # PG jsonb @> equivalent

    # total
    total = (await session.execute(q.with_only_columns(Event.id))).unique().rowcount or 0

    # page
    q = q.order_by(Event.ts.desc(), Event.id.desc()).limit(limit).offset(offset)
    rows = (await session.execute(q)).scalars().all()

    # serialize
    items = [
        {
            "id": str(r.id),
            "project_id": str(r.project_id),
            "name": r.name,
            "ts": r.ts.isoformat() + "Z",
            "user_id": r.user_id,
            "props": r.props,
            "seq": r.seq,
            "idempotency_key": r.idempotency_key,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
    return items, total

async def list_events_keyset(
    session: AsyncSession,
    project_id: str,
    limit: int,
    after_ts: datetime,
    after_id: str,
    name: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    props_contains: Optional[Dict[str, Any]] = None,
):
    q = select(Event).where(Event.project_id == _uuid.UUID(project_id))
    if name:
        q = q.where(Event.name.in_(name))
    if user_id:
        q = q.where(Event.user_id == user_id)
    if since:
        q = q.where(Event.ts >= since)
    if until:
        q = q.where(Event.ts < until)
    if props_contains:
        from sqlalchemy import func
        q = q.where(func.jsonb_contains(Event.props, props_contains))

    # keyset (ts DESC, id DESC)
    q = q.where(
        (Event.ts < after_ts) |
        ((Event.ts == after_ts) & (Event.id < _uuid.UUID(after_id)))
    ).order_by(Event.ts.desc(), Event.id.desc()).limit(limit)

    rows = (await session.execute(q)).scalars().all()
    items = [
        {
            "id": str(r.id),
            "project_id": str(r.project_id),
            "name": r.name,
            "ts": r.ts.isoformat() + "Z",
            "user_id": r.user_id,
            "props": r.props,
            "seq": r.seq,
            "idempotency_key": r.idempotency_key,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
    next_cursor = None
    if items:
        last = rows[-1]
        next_cursor = {
            "after_ts": last.ts.isoformat() + "Z",
            "after_id": str(last.id),
        }
    return items, next_cursor
