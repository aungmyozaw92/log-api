import os
from rq import Queue
from redis import Redis


def get_redis() -> Redis:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(url)


def get_queue(name: str = "default") -> Queue:
    return Queue(name, connection=get_redis())


