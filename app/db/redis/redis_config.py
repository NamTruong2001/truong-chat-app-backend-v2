from redis import Redis

from util import get_settings
import redis
import time
from redis.exceptions import ConnectionError


def connect_to_redis_with_retry() -> Redis:
    settings = get_settings()
    redis_client = None
    wait_time = 1  # Initial wait time in seconds

    for i in range(3):  # Retry up to 10 times
        try:
            redis_client = redis.Redis(
                password=(
                    settings.redis_password if not settings.redis_password else None
                ),
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
            )
            # Try a simple command to check the connection
            redis_client.ping()
            break  # If the command succeeded, break the loop
        except ConnectionError:
            print(f"Failed to connect to Redis, retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2  # Double the wait time for the next attempt

    if redis_client is None:
        raise Exception("Failed to connect to Redis after multiple attempts")

    return redis_client
