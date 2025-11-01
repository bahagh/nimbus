from __future__ import annotations
import hmac, hashlib, time, logging, json
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nimbus.db import get_session
from nimbus.models.project import Project
from nimbus.schemas.events import IngestRequest
from nimbus.settings import settings

log = logging.getLogger(__name__)

def _hex_hmac(ts: str, method: str, path: str, body: bytes, secret: str) -> str:
    msg = f"{ts}:{method}:{path}:{body.decode()}"
    return hmac.new(secret.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest()

async def verify_ingest_signature(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> bool:
    headers = request.headers
    kid = headers.get("x-api-key-id")
    ts  = headers.get("x-api-timestamp")
    sig = headers.get("x-api-signature")

    if not kid or not ts or not sig:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing HMAC headers")

    log.warning("HMAC: received kid=%r ts=%r sig[0:8]=%s...", kid, ts, sig[:8])

    res = await session.execute(select(Project).where(Project.api_key_id == kid))
    project = res.scalar_one_or_none()
    if not project:
        log.warning("HMAC: no project for kid=%r", kid)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown API key id")

    now = int(time.time())
    try:
        ts_int = int(ts)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad X-Api-Timestamp")
    if abs(now - ts_int) > 300:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Stale X-Api-Timestamp")

    raw_body = await request.body()

    expected = _hex_hmac(ts, request.method, request.url.path, raw_body, settings.get_ingest_secret())
    if not hmac.compare_digest(expected, sig):
        log.warning("HMAC: signature mismatch kid=%s", kid)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad signature")

    try:
        body_obj = json.loads(raw_body.decode())
        if body_obj.get("project_id") != str(project.id):
            raise HTTPException(status_code=401, detail="project_id/kid mismatch")
    except Exception:
        pass

    return True
