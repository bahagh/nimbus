import json
import hmac
import hashlib
import time
from typing import Tuple, Any, Optional

from fastapi import Request, HTTPException, status


def _get_header(request: Request, name: str) -> Optional[str]:
    # Headers are case-insensitive; FastAPI exposes a dict-like
    return request.headers.get(name)


async def verify_hmac_request(
    request: Request,
    raw_body: bytes | None = None,
) -> Tuple[str, str, dict]:
    """
    Dev-friendly HMAC verifier that accepts an optional raw_body so the caller
    doesn't have to read the stream twice.

    Returns: (api_key_id, project_id, body_json_dict)
    """
    # 1) Read body exactly once
    body_bytes = raw_body or await request.body()
    try:
        body_text = body_bytes.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Body must be utf-8")

    # 2) Required headers
    api_key_id = _get_header(request, "X-Api-Key-Id")
    ts = _get_header(request, "X-Api-Timestamp")
    sig = _get_header(request, "X-Api-Signature")
    if not api_key_id or not ts or not sig:
        raise HTTPException(status_code=401, detail="Missing HMAC headers")

    # 3) Timestamp freshness (±300s)
    try:
        ts_int = int(ts)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid timestamp")
    now = int(time.time())
    if abs(now - ts_int) > 300:
        raise HTTPException(status_code=401, detail="Stale request")

    # 4) Resolve secret (DEV MODE: local key only)
    # In your current setup you ingest with: local-key-id / local-super-secret
    # For project-specific secrets, extend this to fetch the secret for api_key_id.
    if api_key_id == "local-key-id":
        import os
        secret = os.environ.get("API_KEY_SECRET", "local-super-secret")
    else:
        # Not implemented yet for per-project secrets
        raise HTTPException(status_code=401, detail="Unknown API key id")

    # 5) Recompute signature: "{ts}:{method}:{path}:{body}"
    method = request.method.upper()
    # raw_path includes query; HMAC was specified against the path only
    path = request.url.path
    signed = f"{ts}:{method}:{path}:{body_text}".encode("utf-8")
    expect = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expect, sig):
        raise HTTPException(status_code=401, detail="Bad signature")

    # 6) Parse JSON and pull project_id
    try:
        body_json = json.loads(body_text)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    project_id = body_json.get("project_id")
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")

    return api_key_id, project_id, body_json
