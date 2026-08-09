from abc import ABC, abstractmethod

class IAvailabilityService(ABC):
    @abstractmethod
    async def check_meal_availability(self, restaurent_id: str, date: str, time_slot: str) -> bool:
        pass
    @abstractmethod
    async def check_time_slot_availability(self, restaurent_id: str, date: str, time_slot: str) -> bool:
        pass
    @abstractmethod
    async def get_available_time_slots(self, restaurent_id: str, date: str) -> list[str]:
        pass
    @abstractmethod
    async def reserve_meal_quantity(self, restaurent_id: str, date: str, time_slot: str, quantity: int) -> bool:
        pass
    @abstractmethod
    async def release_meal_quantity(self, restaurent_id: str, date: str, time_slot: str, quantity: int) -> bool:
        pass
    @abstractmethod
    async def reserve_time_slot(self, restaurent_id: str, date: str, time_slot: str) -> bool:
        pass
    @abstractmethod
    async def release_time_slot(self, restaurent_id: str, date: str, time_slot: str) -> bool:
        pass
    