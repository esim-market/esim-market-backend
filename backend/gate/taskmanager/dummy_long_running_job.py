import asyncio

from backend.common.logging import get_logger
from backend.common.mongodb_lifecycle_mixin import MongoDbLifecycleMixin
from backend.common.redis_lifecycle_mixin import RedisLifecycleMixin
from .job_base import JobBase

logger = get_logger(__name__)


class DummyLongRunningJob(JobBase, MongoDbLifecycleMixin, RedisLifecycleMixin):
    def __init__(self, interval: float = 30.0):
        self.interval = interval
        self.stop_event = asyncio.Event()

    async def run(self) -> None:
        logger.info("job started")
        try:
            while not self.stop_event.is_set():
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=self.interval)
                except asyncio.TimeoutError:
                    logger.info("dummy job heartbeat")
        except asyncio.CancelledError:
            logger.info("cancellation requested")
            raise
        finally:
            logger.info("job stopped")

    def request_stop(self) -> None:
        self.stop_event.set()

    async def dispose(self) -> None:
        self.request_stop()
        await self.close_redis()
        await self.close_mongodb()
