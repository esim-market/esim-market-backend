from .esim_seller_repository_base import EsimSellerRepositoryBase


class EsimXYZRepository(EsimSellerRepositoryBase):
    async def list_products(self, *args, **kwargs): raise NotImplementedError("Seller integration is deferred")
    async def place_order(self, *args, **kwargs): raise NotImplementedError("Seller integration is deferred")
