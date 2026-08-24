from collections.abc import Sequence

from beanie import Document, init_beanie
from pymongo import AsyncMongoClient

from backend.common.env.settings import MongoSettings


class MongoDbLifecycleMixin:
    async def open_mongodb(
        self,
        settings: MongoSettings | None = None,
        document_models: Sequence[type[Document]] = (),
    ) -> None:
        config = settings or MongoSettings()
        client = AsyncMongoClient(config.MONGO_DSN)
        self.mongodb_client = client
        try:
            await client.admin.command("ping")
            await init_beanie(
                database=client[config.MONGO_DB_NAME],
                document_models=list(document_models),
            )
        except Exception:
            await client.close()
            self.mongodb_client = None
            raise

    async def close_mongodb(self) -> None:
        client = getattr(self, "mongodb_client", None)
        if client is not None:
            await client.close()
            self.mongodb_client = None
