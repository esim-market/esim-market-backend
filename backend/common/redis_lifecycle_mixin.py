from redis.asyncio import Redis
from redis.asyncio.sentinel import Sentinel

from backend.common.env.redis_env_settings import RedisEnvSettings, RedisKind
from backend.repository.redis import RedisRepositoryFactory, RedisSentinelConnectionModel


class RedisLifecycleMixin:
    """Reusable async Redis resource lifecycle for process gates."""

    async def open_redis(self, settings: RedisEnvSettings | None = None) -> None:
        config = (settings or RedisEnvSettings()).core_cluster_config
        common = {
            "password": config.password,
            "decode_responses": config.decode_responses,
            "socket_timeout": config.socket_timeout,
            "socket_connect_timeout": config.socket_connect_timeout,
        }
        if config.kind is RedisKind.SENTINEL:
            sentinel = Sentinel(config.sentinel_hosts or [(config.host, config.port)], **common)
            connection = RedisSentinelConnectionModel(
                sentinel=sentinel,
                master=sentinel.master_for(config.sentinel_master_alias, **common),
                slave=sentinel.slave_for(config.sentinel_master_alias, **common),
            )
            kind = RedisKind.SENTINEL
        else:
            connection = Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                max_connections=config.connection_pool_max_connections,
                **common,
            )
            kind = RedisKind.STAND_ALONE

        self.redis_connection = connection
        self.redis_repository_factory = RedisRepositoryFactory(connection)
        self.redis_repository = self.redis_repository_factory.create_repository(kind)

    async def close_redis(self) -> None:
        connection = getattr(self, "redis_connection", None)
        if connection is None:
            return

        clients = [connection] if isinstance(connection, Redis) else [connection.master, connection.slave]
        for client in clients:
            await client.aclose()
        if not isinstance(connection, Redis):
            await connection.sentinel.close()
        self.redis_connection = None
        self.redis_repository_factory = None
        self.redis_repository = None
