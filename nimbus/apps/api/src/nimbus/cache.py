import redis.asyncio as aioredis
from typing import Optional

from .settings import settings

# Redis connection - may fail if Redis is not running
redis: Optional[aioredis.Redis] = None

try:
    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
except Exception as e:
    import logging
    logging.warning(f"Redis connection failed (will operate without cache): {e}")
    redis = None
