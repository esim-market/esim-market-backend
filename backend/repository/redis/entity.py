from dataclasses import dataclass

from redis.asyncio import Redis
from redis.asyncio.sentinel import Sentinel


@dataclass(slots=True)
class RedisSentinelConnectionModel:
    sentinel: Sentinel
    master: Redis
    slave: Redis
