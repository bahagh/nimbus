import hmac
import hashlib
from fastapi import Header, HTTPException, status, Request
from nimbus.settings import settings

def _hex_hmac(ts: str, method: str, path: str, body: str, secret: str) -> str:
    msg = f"{ts}:{method.upper()}:{path}:{body}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

async def verify_ingest_signature(
    request: Request,
    x_api_key_id: str = Header(..., alias="X-Api-Key-Id"),
    x_api_timestamp: str = Header(..., alias="X-Api-Timestamp"),
    x_api_signature: str = Header(..., alias="X-Api-Signature"),
):
    # get raw body bytes to ensure exact signature match
    raw = await request.body()
    body = raw.decode("utf-8")

    if x_api_key_id != settings.ingest_api_key_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown API key id")

    expected = _hex_hmac(x_api_timestamp, request.method, request.url.path, body, settings.ingest_api_key_secret)
    if not hmac.compare_digest(expected, x_api_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad signature")
    return True
