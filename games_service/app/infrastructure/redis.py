import redis.asyncio as redis

from config.settings import settings


redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


def get_redis_client():
    return redis_client
