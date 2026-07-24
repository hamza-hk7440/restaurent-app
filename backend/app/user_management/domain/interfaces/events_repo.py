from abc import ABC, abstractmethod
from user_management.domain.interfaces.base import DomainEvent

class IEventRepository(ABC):
    @abstractmethod
    async def dispatch(self, event: DomainEvent) -> None:
        pass