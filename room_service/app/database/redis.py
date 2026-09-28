from redis.asyncio import Redis

from app.core import config

_redis_client: Redis | None = None


def create_redis_client() -> Redis:
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis(
            host=config.settings.redis_host,
            port=config.settings.redis_port,
            db=getattr(config.settings, "redis_db", 0),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

    return _redis_client


def get_redis_client() -> Redis:
    return _redis_client or create_redis_client()


async def close_redis_client() -> None:
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
    
