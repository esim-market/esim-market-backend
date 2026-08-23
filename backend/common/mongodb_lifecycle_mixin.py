from beanie import init_beanie
from pymongo import AsyncMongoClient

from backend.common.env.settings import MongoSettings


class MongoDbLifecycleMixin:
    async def open_mongodb(self, settings: MongoSettings | None = None) -> None:
        config = settings or MongoSettings()
        client = AsyncMongoClient(config.uri)
        await client.admin.command("ping")
        await init_beanie(database=client[config.database], document_models=[])
        self.mongodb_client = client

    async def close_mongodb(self) -> None:
        client = getattr(self, "mongodb_client", None)
        if client is not None:
            await client.close()
            self.mongodb_client = None
