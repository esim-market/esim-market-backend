import httpx

from .esim_seller_repository_base import EsimSellerRepositoryBase


class EsimConnectRepository(EsimSellerRepositoryBase):
    async def list_products(self, *args, **kwargs): raise NotImplementedError("eSIM Connect SDK integration is deferred")
    async def place_order(self, *args, **kwargs): raise NotImplementedError("eSIM Connect SDK integration is deferred")
