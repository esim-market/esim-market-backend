from abc import ABC, abstractmethod
from enum import StrEnum

import httpx


class EsimSellerType(StrEnum):
    ESIM_CONNECT = "ESIM_CONNECT"
    ESIM_XYZ = "ESIM_XYZ"


class EsimSellerRepositoryBase(ABC):
    def __init__(self, http_client: httpx.AsyncClient): self.http_client = http_client

    @abstractmethod
    async def list_products(self, *args, **kwargs): ...

    @abstractmethod
    async def place_order(self, *args, **kwargs): ...
