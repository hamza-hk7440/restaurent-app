from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.reservation_item_entity import ReservationItemEntity

class IReservationItemRepository(ABC):
    @abstractmethod
    async def create(self, reservation_item: ReservationItemEntity) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, reservation_item_id: str) -> Optional[ReservationItemEntity]:
        pass

    @abstractmethod
    async def get_by_reservation(self, reservation_id: str) -> list[ReservationItemEntity]:
        pass
    @abstractmethod
    async def update(self, reservation_item: ReservationItemEntity) -> str:
        pass
    @abstractmethod
    async def delete(self, reservation_item_id: str) -> str:
        pass