import time
from functools import lru_cache

import jwt

from ..config import settings
from .oidc import OIDCVerifier


def create_token(sub: str, ttl: int) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + ttl,
        "aud": settings.oidc_audience or "nimbus-local",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


@lru_cache(maxsize=8)
def _get_verifier(issuer: str, audience: str) -> OIDCVerifier:
    return OIDCVerifier(issuer=issuer, audience=audience)


def decode_token(token: str) -> dict | None:
    # Prefer OIDC/JWKS if configured (RS256)
    if settings.oidc_issuer and settings.oidc_audience:
        try:
            return _get_verifier(settings.oidc_issuer, settings.oidc_audience).verify(token)
        except Exception:
            pass  # fall back to local HS*

    # Fallback to local HS256/HS512
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
            audience=settings.oidc_audience or "nimbus-local",
        )
    except Exception:
        return None
