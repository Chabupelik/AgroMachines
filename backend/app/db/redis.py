from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from app.core.config import settings

_redis_client: redis.Redis | None = None


def get_raw_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    yield get_raw_redis_client()


RedisClient = Annotated[redis.Redis, Depends(get_redis)]
