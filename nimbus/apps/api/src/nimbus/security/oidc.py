from functools import lru_cache

import jwt
import requests


class OIDCVerifier:
    def __init__(self, issuer: str, audience: str):
        self.issuer = issuer
        self.audience = audience
        self._cfg = requests.get(issuer, timeout=5).json()
        self._jwks = requests.get(self._cfg["jwks_uri"], timeout=5).json()

    @lru_cache(maxsize=128)
    def _kid_to_key(self, kid: str):
        for k in self._jwks["keys"]:
            if k["kid"] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(k)
        raise ValueError("kid not found")

    def verify(self, token: str) -> dict | None:
        unverified = jwt.get_unverified_header(token)
        key = self._kid_to_key(unverified["kid"])
        return jwt.decode(token, key=key, algorithms=["RS256"], audience=self.audience)
