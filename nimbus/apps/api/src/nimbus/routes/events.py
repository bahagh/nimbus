from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from nimbus.schemas.events import IngestRequest, IngestResponse
from nimbus.security.hmac import verify_ingest_signature
from nimbus.services.events import ingest_events
from nimbus.db import get_session
from nimbus.security.jwt import require_jwt
from nimbus.settings import settings
from nimbus.repositories.events import (
    list_events_offset,
    list_events_keyset,
)

router = APIRouter(prefix="/v1", tags=["events"])

# Rate limiter - enabled based on settings
limiter = Limiter(key_func=get_remote_address) if settings.rate_limit_enabled else None


@router.post("/events", response_model=IngestResponse, summary="Ingest a batch of events (HMAC-signed)")
async def ingest(
    request: Request,
    payload: IngestRequest,
    _sig_ok: bool = Depends(verify_ingest_signature),
    session: AsyncSession = Depends(get_session),
):
    # Apply rate limiting if enabled
    if limiter and settings.rate_limit_enabled:
        # Higher rate limit for ingestion endpoint
        @limiter.limit(f"{settings.rate_limit_per_minute * 2}/minute")
        async def _rate_limited_ingest(request: Request):
            pass
        await _rate_limited_ingest(request)

    import logging
    if not payload.project_id:
        raise HTTPException(status_code=400, detail="Missing project_id")
    if not payload.events or not isinstance(payload.events, list) or len(payload.events) == 0:
        raise HTTPException(status_code=400, detail="No events provided")
    try:
        accepted = await ingest_events(session, payload.project_id, [e.model_dump() for e in payload.events])
        logging.info(f"Ingested {accepted} events for project {payload.project_id}")
        return IngestResponse(accepted=accepted)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Ingestion error for project {payload.project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ingestion failed")


@router.get("/events", summary="List events (JWT protected) with filtering + pagination")
async def get_events(
    request: Request,
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
    # Apply rate limiting if enabled
    if limiter and settings.rate_limit_enabled:
        @limiter.limit(f"{settings.rate_limit_per_minute}/minute")
        async def _rate_limited_get(request: Request):
            pass
        await _rate_limited_get(request)

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

    import uuid
    try:
        project_uuid = uuid.UUID(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id (must be UUID)")

    # keyset mode
    if after_ts or after_id:
        if not (after_ts and after_id):
            raise HTTPException(status_code=400, detail="Provide both after_ts and after_id for keyset pagination")
        items, next_cursor = await list_events_keyset(
            session,
            project_id=str(project_uuid),
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
        project_id=str(project_uuid),
        limit=limit,
        offset=off,
        name=name,
        user_id=user_id,
        since=since,
        until=until,
        props_contains=props_contains,
    )
    return {"items": items, "count": total, "limit": limit, "offset": off}
