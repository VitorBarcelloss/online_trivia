from redis import Redis


def create_redis_client(redis_url: str) -> Redis: ...


def get_redis_client() -> Redis: ...
