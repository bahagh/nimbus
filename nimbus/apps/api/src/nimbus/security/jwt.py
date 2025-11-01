import time
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from nimbus.settings import settings

_http_bearer = HTTPBearer(auto_error=False)

def _now_epoch() -> int:
    return int(time.time())  # UTC epoch seconds

def _encode(payload: dict, ttl_seconds: int) -> str:
    now = _now_epoch()
    body = {
        **payload,
        "iat": now,
        "exp": now + int(ttl_seconds),
        "iss": settings.app_name,
    }
    return jwt.encode(body, settings.get_jwt_secret(), algorithm=settings.jwt_algorithm)

def create_access_token(sub: str) -> str:
    return _encode({"sub": sub, "typ": "access"}, settings.jwt_access_ttl_seconds)

def create_refresh_token(sub: str) -> str:
    return _encode({"sub": sub, "typ": "refresh"}, settings.jwt_refresh_ttl_seconds)

def _decode(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.get_jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "iss"]},
            leeway=5,  # small clock skew tolerance
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def require_jwt(creds: HTTPAuthorizationCredentials = Depends(_http_bearer)) -> dict:
    if not creds or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    claims = _decode(creds.credentials)
    if claims.get("typ") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")
    return claims

async def require_refresh_jwt(creds: HTTPAuthorizationCredentials = Depends(_http_bearer)) -> dict:
    if not creds or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    claims = _decode(creds.credentials)
    if claims.get("typ") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")
    return claims
