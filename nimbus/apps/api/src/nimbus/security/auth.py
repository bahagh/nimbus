import time
from functools import lru_cache

import jwt

from nimbus.settings import settings
from .oidc import OIDCVerifier


def create_token(sub: str, ttl: int, typ: str = "access") -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + ttl,
        "iss": settings.app_name,
        "typ": typ,
    }
    # Handle both Settings with get_jwt_secret() method and plain string jwt_secret
    secret = settings.get_jwt_secret() if hasattr(settings, 'get_jwt_secret') else settings.jwt_secret
    return jwt.encode(payload, secret, algorithm=settings.jwt_alg)


@lru_cache(maxsize=8)
def _get_verifier(issuer: str, audience: str) -> OIDCVerifier:
    return OIDCVerifier(issuer=issuer, audience=audience)


def decode_token(token: str) -> dict | None:
    # Prefer OIDC/JWKS if configured (RS256)
    if settings.oidc_issuer and settings.oidc_audience:
        try:
            return _get_verifier(settings.oidc_issuer, settings.oidc_audience).verify(token)
        except Exception:
            pass

    # Fallback to local HS256/HS512
    try:
        # Handle both Settings with get_jwt_secret() method and plain string jwt_secret
        secret = settings.get_jwt_secret() if hasattr(settings, 'get_jwt_secret') else settings.jwt_secret
        return jwt.decode(
            token,
            secret,
            algorithms=[settings.jwt_alg],
        )
    except Exception:
        return None
