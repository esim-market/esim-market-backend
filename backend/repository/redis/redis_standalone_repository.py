from redis.asyncio import Redis

from .history_repository_mixin import HistoryRepositoryMixin
from .redis_base_repository import RedisBaseRepository


class RedisStandAloneRepository(HistoryRepositoryMixin, RedisBaseRepository):
    def __init__(self, conn: Redis):
        self.conn = conn

    def _read(self) -> Redis: return self.conn
    def _write(self) -> Redis: return self.conn
