from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.time_slot_availability_entity import TimeSlotAvailabilityEntity

class ITimeSlotAvailabilityRepository(ABC):
    @abstractmethod
    async def create(self, time_slot_availability: TimeSlotAvailabilityEntity) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, time_slot_availability_id: str) -> Optional[TimeSlotAvailabilityEntity]:
        pass

    @abstractmethod
    async def get_by_slot_date(self, time_slot_id: str, date: datetime) -> Optional[TimeSlotAvailabilityEntity]:
        pass
    @abstractmethod
    async def get_by_slot(self, time_slot_id: str) -> list[TimeSlotAvailabilityEntity]:
        pass
    @abstractmethod
    async def reserve_slot(self, time_slot_availability_id: str, quantity: int) -> str:
        pass
    @abstractmethod
    async def release_slot(self, time_slot_availability_id: str, quantity: int) -> str:
        pass
    @abstractmethod
    async def get_available_slots(self, time_slot_id: str, date: datetime) -> list[TimeSlotAvailabilityEntity]:
        pass
    @abstractmethod
    async def update(self, time_slot_availability: TimeSlotAvailabilityEntity) -> str:
        pass