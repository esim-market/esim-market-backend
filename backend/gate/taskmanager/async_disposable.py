from abc import ABC, abstractmethod


class AsyncDisposable(ABC):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        await self.dispose()

    @abstractmethod
    async def dispose(self) -> None: ...
