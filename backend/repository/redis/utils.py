from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar

from redis.exceptions import ConnectionError, DataError, ResponseError, TimeoutError
from redis.sentinel import MasterNotFoundError

P = ParamSpec("P")
T = TypeVar("T")


class RedisRepositoryError(RuntimeError):
    """Stable repository-level error for Redis transport failures."""


def redis_exception_catch_func(exc: Exception) -> RedisRepositoryError:
    if isinstance(exc, MasterNotFoundError):
        return RedisRepositoryError("Cannot connect to Redis: master not found")
    if isinstance(exc, ConnectionError):
        return RedisRepositoryError("Cannot connect to Redis")
    if isinstance(exc, TimeoutError):
        return RedisRepositoryError("Cannot connect to Redis: timeout")
    if isinstance(exc, DataError):
        return RedisRepositoryError("Redis data error")
    if isinstance(exc, ResponseError):
        return RedisRepositoryError("Redis response error")
    return RedisRepositoryError(f"Redis operation failed: {type(exc).__name__}")


def retry_on_failure_async(max_retries: int = 3, delay: float = 0.25):
    """Retry transient Redis operations and expose a project-owned exception."""
    import asyncio

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError, MasterNotFoundError) as exc:
                    if attempt + 1 == max_retries:
                        raise redis_exception_catch_func(exc) from exc
                    await asyncio.sleep(delay)
                except (DataError, ResponseError) as exc:
                    raise redis_exception_catch_func(exc) from exc
        return wrapped
    return decorator
