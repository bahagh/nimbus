import redis.asyncio as aioredis

from .config import settings

redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
