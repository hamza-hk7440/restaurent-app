from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.value_objects.restaurent_status import RestaurentStatus
from reservation.domain.entities.restaurents_entity import Restaurent

class IRestaurentRepository(ABC):
    @abstractmethod
    async def create(self, restaurent: Restaurent) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, restaurent_id: str) -> Optional[Restaurent]:
        pass

    @abstractmethod
    async def get_by_establishment(self, establishment_id: str) -> Optional[Restaurent]:
        pass
    @abstractmethod
    async def get_all(self) -> list[Restaurent]:
        pass
    @abstractmethod
    async def update(self, restaurent: Restaurent) -> str:
        pass
    @abstractmethod
    async def delete(self, restaurent_id: str) -> str:
        pass
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Restaurent]:
        pass
    @abstractmethod
    async def get_open_restaurants(self) -> list[Restaurent]:
        pass
    @abstractmethod
    async def update_status(self, restaurent_id: str, status: RestaurentStatus) -> str:
        pass