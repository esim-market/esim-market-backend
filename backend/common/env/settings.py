from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    DEBUG: Optional[bool] = Field(default=True)

    MONGO_DSN: Optional[str] = Field(default=None)
    MONGO_ENDPOINT: str
    MONGO_DB_NAME: str = Field(default="esim_market")
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_REPL: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def maybe_parse_url(self) -> "MongoSettings":
        if self.MONGO_DSN is None:
            credentials = ""
            if self.MONGO_USER and self.MONGO_PASS:
                credentials = f"{self.MONGO_USER}:{self.MONGO_PASS}@"

            mongo_dsn = (
                f"mongodb://{credentials}"
                f"{self.MONGO_ENDPOINT}/"
                f"{self.MONGO_DB_NAME}"
                f"?authSource={self.MONGO_DB_NAME}"
            )

            if self.MONGO_REPL:
                mongo_dsn = f"{mongo_dsn}&replicaSet={self.MONGO_REPL}"

            self.MONGO_DSN = mongo_dsn

        return self


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
    root_path: str = ""
