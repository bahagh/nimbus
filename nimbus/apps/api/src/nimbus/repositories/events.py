from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, and_, func, cast
from sqlalchemy.dialects.postgresql import insert as pg_insert, JSONB
from sqlalchemy import insert as sa_insert
from sqlalchemy.ext.asyncio import AsyncSession

from nimbus.models.event import Event


async def bulk_insert_events(session: AsyncSession, records: list[dict]):
    if not records:
        return
    cleaned = [{k: v for k, v in r.items() if not (k == "seq" and v is None)} for r in records]

    if session.bind and session.bind.dialect.name == "postgresql":
        has_seq = any(r.get("seq") is not None for r in cleaned)
        stmt = pg_insert(Event).values(cleaned)
        if has_seq:
            # if you later add a unique index (project_id, seq), do nothing on conflicts
            stmt = stmt.on_conflict_do_nothing(index_elements=[Event.project_id, Event.seq])
        await session.execute(stmt)
        return

    # SQLite (dev only)
    stmt = sa_insert(Event).values(cleaned)
    await session.execute(stmt)


def _normalize_dt(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert aware datetimes to UTC-naive to match TIMESTAMP WITHOUT TIME ZONE columns.
    Leave naive as-is.
    """
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _apply_filters(
    stmt,
    *,
    project_id: str,
    name: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    props_contains: Optional[dict] = None,
):
    since = _normalize_dt(since)
    until = _normalize_dt(until)

    conds = [Event.project_id == project_id]
    if name:
        conds.append(Event.name.in_(name))
    if user_id:
        conds.append(Event.user_id == user_id)
    if since:
        conds.append(Event.ts >= since)
    if until:
        conds.append(Event.ts < until)
    if props_contains:
        stmt = stmt.where(cast(Event.props, JSONB).contains(props_contains))
    if conds:
        stmt = stmt.where(and_(*conds))
    return stmt


async def list_events_offset(
    session: AsyncSession,
    *,
    project_id: str,
    limit: int = 50,
    offset: int = 0,
    name: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    props_contains: Optional[dict] = None,
) -> Tuple[List[Dict], int]:
    # total
    count_stmt = select(func.count()).select_from(Event)
    count_stmt = _apply_filters(
        count_stmt,
        project_id=project_id,
        name=name,
        user_id=user_id,
        since=since,
        until=until,
        props_contains=props_contains,
    )
    total = (await session.execute(count_stmt)).scalar_one()

    # page
    stmt = select(Event)
    stmt = _apply_filters(
        stmt,
        project_id=project_id,
        name=name,
        user_id=user_id,
        since=since,
        until=until,
        props_contains=props_contains,
    )
    stmt = stmt.order_by(Event.ts.desc(), Event.id.desc()).limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()

    items = [
        {
            "id": str(e.id),
            "project_id": str(e.project_id),
            "name": e.name,
            "ts": e.ts,
            "user_id": e.user_id,
            "seq": e.seq,
            "props": e.props,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        for e in rows
    ]
    return items, int(total)


async def list_events_keyset(
    session: AsyncSession,
    *,
    project_id: str,
    limit: int = 50,
    after_ts: Optional[datetime] = None,
    after_id: Optional[str] = None,
    name: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    props_contains: Optional[dict] = None,
) -> Tuple[List[Dict], Optional[Dict]]:
    after_ts = _normalize_dt(after_ts)

    stmt = select(Event)
    stmt = _apply_filters(
        stmt,
        project_id=project_id,
        name=name,
        user_id=user_id,
        since=since,
        until=until,
        props_contains=props_contains,
    )

    if after_ts and after_id:
        stmt = stmt.where(
            (Event.ts < after_ts) | ((Event.ts == after_ts) & (Event.id < after_id))
        )

    stmt = stmt.order_by(Event.ts.desc(), Event.id.desc()).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()

    items = [
        {
            "id": str(e.id),
            "project_id": str(e.project_id),
            "name": e.name,
            "ts": e.ts,
            "user_id": e.user_id,
            "seq": e.seq,
            "props": e.props,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        for e in rows
    ]

    next_cursor = None
    if items:
        last = items[-1]
        next_cursor = {"after_ts": last["ts"].isoformat(), "after_id": last["id"]}

    return items, next_cursor
