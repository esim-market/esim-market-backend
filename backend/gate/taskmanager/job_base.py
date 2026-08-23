from abc import abstractmethod

from .async_disposable import AsyncDisposable


class JobBase(AsyncDisposable):
    @abstractmethod
    async def run(self) -> None: ...
