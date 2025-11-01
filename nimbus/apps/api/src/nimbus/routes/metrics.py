from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from nimbus.schemas.metrics import MetricsResponse, SeriesPoint
from nimbus.security.jwt import require_jwt
from nimbus.services.metrics import get_event_count_series
from nimbus.db import get_session

router = APIRouter(prefix="/v1", tags=["metrics"])

@router.get("/metrics", response_model=MetricsResponse, summary="Time series metrics (JWT protected)")
async def metrics(
    project_id: str,
    bucket: str = Query("1h", pattern=r"^(1m|5m|15m|1h|1d)$"),
    limit: int = Query(24, ge=1, le=1000),
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    import uuid
    try:
        project_uuid = uuid.UUID(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id (must be UUID)")
    series = await get_event_count_series(session, project_id=str(project_uuid), bucket=bucket, limit=limit)
    return MetricsResponse(metric="events.count", bucket=bucket, series=[SeriesPoint(**p) for p in series])
