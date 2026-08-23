import httpx

from .esim_connect_repository import EsimConnectRepository
from .esim_seller_repository_base import EsimSellerRepositoryBase, EsimSellerType
from .esim_xyz_repository import EsimXYZRepository


class RepositoryFactory:
    def __init__(self):
        self._mapping = {EsimSellerType.ESIM_CONNECT: EsimConnectRepository, EsimSellerType.ESIM_XYZ: EsimXYZRepository}

    def register_mapping(self, seller: EsimSellerType, repository: type[EsimSellerRepositoryBase]) -> None: self._mapping[seller] = repository

    def create(self, seller: EsimSellerType, http_client: httpx.AsyncClient) -> EsimSellerRepositoryBase:
        try: repository = self._mapping[seller]
        except KeyError as exc: raise ValueError(f"Seller repository not registered: {seller}") from exc
        return repository(http_client)
