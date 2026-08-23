from redis.asyncio import Redis

from .entity import RedisSentinelConnectionModel
from .history_repository_mixin import HistoryRepositoryMixin
from .redis_base_repository import RedisBaseRepository


class RedisSentinelRepository(HistoryRepositoryMixin, RedisBaseRepository):
    def __init__(self, conn: RedisSentinelConnectionModel):
        self.conn = conn

    def _read(self) -> Redis: return self.conn.slave
    def _write(self) -> Redis: return self.conn.master
