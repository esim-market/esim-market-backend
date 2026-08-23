from abc import ABC, abstractmethod


class UsecaseBase(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError
