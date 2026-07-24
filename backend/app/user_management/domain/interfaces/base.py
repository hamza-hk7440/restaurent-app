from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T=TypeVar("T")

class IRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abstractmethod
    def get(self, entity_id: str) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        pass
class DomainEvent:
    pass