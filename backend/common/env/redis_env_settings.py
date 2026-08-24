"""Pydantic v2 settings for standalone Redis and Redis Sentinel."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisKind(StrEnum):
    STAND_ALONE = "STAND_ALONE"
    SENTINEL = "SENTINEL"


class RedisClusterConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(default=6379, ge=1, le=65535)
    password: str | None = None
    db: int = Field(default=0, ge=0)
    decode_responses: bool = True
    connection_pool_max_connections: int = Field(default=100, ge=1)
    socket_timeout: float | None = Field(default=5.0, gt=0)
    socket_connect_timeout: float | None = Field(default=5.0, gt=0)
    kind: RedisKind = RedisKind.STAND_ALONE
    sentinel_hosts: list[tuple[str, int]] = Field(default_factory=list)
    sentinel_master_alias: str = "mymaster"


class RedisEnvSettings(BaseSettings):
    """Settings loaded from REDIS_* variables using nested ``__`` names."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    core_cluster_config: RedisClusterConfig = Field(default_factory=RedisClusterConfig)


RedisSettings = Annotated[RedisEnvSettings, "Redis environment settings"]
