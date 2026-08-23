import asyncio
import signal

from backend.common.env.redis_env_settings import RedisEnvSettings
from backend.common.env.settings import MongoSettings
from backend.common.logging import configure_logging, get_logger
from .dummy_long_running_job import DummyLongRunningJob

logger = get_logger(__name__)


async def main() -> None:
    configure_logging()
    job = DummyLongRunningJob()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, job.request_stop)
    try:
        try:
            await job.open_mongodb(MongoSettings())
        except Exception:
            logger.exception("MongoDB is unavailable during job startup")
        try:
            await job.open_redis(RedisEnvSettings())
        except Exception:
            logger.exception("Redis is unavailable during job startup")
        async with job:
            await job.run()
    finally:
        await job.dispose()


if __name__ == "__main__":
    asyncio.run(main())
