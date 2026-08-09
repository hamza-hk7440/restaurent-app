from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.reservation_modification_entity import ReservationModificationEntity
from reservation.domain.value_objects.reservation_modification_type import ReservationModificationType

class IReservationModificationRepository(ABC):
    @abstractmethod
    async def create(self, reservation_modification: ReservationModificationEntity) -> str:
        pass

    @abstractmethod
    async def get_by_reservation(self, reservation_id: str) -> list[ReservationModificationEntity]:
        pass
    @abstractmethod
    async def get_by_type(self, reservation_id: str, modification_type: ReservationModificationType) -> list[ReservationModificationEntity]:
        pass