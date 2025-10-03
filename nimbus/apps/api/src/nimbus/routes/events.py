from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nimbus.schemas.events import IngestRequest, IngestResponse
from nimbus.security.hmac import verify_ingest_signature
from nimbus.services.events import ingest_events
from nimbus.db import get_session
from nimbus.security.jwt import require_jwt
from nimbus.repositories.events import (
    list_events_offset,
    list_events_keyset,
)

router = APIRouter(prefix="/v1", tags=["events"])


@router.post("/events", response_model=IngestResponse, summary="Ingest a batch of events (HMAC-signed)")
async def ingest(
    payload: IngestRequest,
    _sig_ok: bool = Depends(verify_ingest_signature),
    session: AsyncSession = Depends(get_session),
):
    accepted = await ingest_events(session, payload.project_id, [e.model_dump() for e in payload.events])
    return IngestResponse(accepted=accepted)


@router.get("/events", summary="List events (JWT protected) with filtering + pagination")
async def get_events(
    project_id: str,
    # filtering
    name: Optional[List[str]] = Query(None, description="Filter by name; repeatable: &name=a&name=b"),
    user_id: Optional[str] = None,
    since: Optional[datetime] = Query(None, description="ISO8601 start (inclusive)"),
    until: Optional[datetime] = Query(None, description="ISO8601 end (exclusive)"),
    props: Optional[str] = Query(None, description='JSON filter for props, e.g. {"plan":"pro"}'),
    # pagination: choose one mode
    limit: int = Query(50, ge=1, le=200),
    offset: Optional[int] = Query(None, ge=0, description="Offset-based pagination"),
    after_ts: Optional[datetime] = Query(None, description="Keyset cursor timestamp"),
    after_id: Optional[str] = Query(None, description="Keyset cursor event id (uuid)"),
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    # parse props JSON if provided
    props_contains = None
    if props:
        import json
        try:
            props_contains = json.loads(props)
            if not isinstance(props_contains, dict):
                raise ValueError
        except Exception:
            raise HTTPException(status_code=400, detail="props must be a JSON object")

    # avoid mixing modes
    if (after_ts or after_id) and offset is not None:
        raise HTTPException(status_code=400, detail="Use either offset or keyset params, not both")

    # keyset mode
    if after_ts or after_id:
        if not (after_ts and after_id):
            raise HTTPException(status_code=400, detail="Provide both after_ts and after_id for keyset pagination")
        items, next_cursor = await list_events_keyset(
            session,
            project_id=project_id,
            limit=limit,
            after_ts=after_ts,
            after_id=after_id,
            name=name,
            user_id=user_id,
            since=since,
            until=until,
            props_contains=props_contains,
        )
        return {"items": items, "next_cursor": next_cursor}

    # default: offset mode
    off = offset or 0
    items, total = await list_events_offset(
        session,
        project_id=project_id,
        limit=limit,
        offset=off,
        name=name,
        user_id=user_id,
        since=since,
        until=until,
        props_contains=props_contains,
    )
    return {"items": items, "count": total, "limit": limit, "offset": off}
