from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.time_slot_entity import TimeSlotEntity
class ITimeSlotRepository(IRepository):
    @abstractmethod
    async def create(self, time_slot: TimeSlotEntity) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, time_slot_id: str) -> Optional[TimeSlotEntity]:
        pass
    @abstractmethod
    async def get_by_restaurent(self, restaurent_id: str) -> list[TimeSlotEntity]:
        pass
    @abstractmethod
    async def get_by_restaurent_time(self, restaurent_id: str, time: datetime) -> Optional[TimeSlotEntity]:
        pass
    @abstractmethod
    async def get_active_slots(self, restaurent_id: str) -> list[TimeSlotEntity]:
        pass
    @abstractmethod
    async def update(self, time_slot: TimeSlotEntity) -> str:
        pass
    @abstractmethod
    async def delete(self, time_slot_id: str) -> str:
        pass
    @abstractmethod
    async def activate_slot(self, time_slot_id: str) -> str:
        pass
    @abstractmethod
    async def deactivate_slot(self, time_slot_id: str) -> str:
        pass