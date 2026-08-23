from collections.abc import Callable

from redis.asyncio import Redis

from backend.common.env.redis_env_settings import RedisKind

from .entity import RedisSentinelConnectionModel
from .redis_base_repository import RedisBaseRepository
from .redis_sentinel_repository import RedisSentinelRepository
from .redis_standalone_repository import RedisStandAloneRepository


class RedisRepositoryFactory:
    """Mapping-based repository selector retained from the reference design."""

    def __init__(self, conn: Redis | RedisSentinelConnectionModel):
        self.conn = conn
        self._repos: dict[RedisKind, type[RedisBaseRepository]] = {}
        self.init_mapping()

    def register_mapping(self, key: RedisKind, creator: type[RedisBaseRepository]) -> None:
        self._repos[key] = creator

    def init_mapping(self) -> None:
        self.register_mapping(RedisKind.STAND_ALONE, RedisStandAloneRepository)
        self.register_mapping(RedisKind.SENTINEL, RedisSentinelRepository)

    def create_repository(self, key: RedisKind, **kwargs) -> RedisBaseRepository:
        try: repository = self._repos[key]
        except KeyError as exc: raise ValueError(f"Redis repository not registered for: {key}") from exc
        return repository(conn=kwargs.get("conn", self.conn))
