from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.meal_availability_entity import MealAvailabilityEntity

class IMealAvailabilityRepository(ABC):
    @abstractmethod
    async def create(self, meal_availability: MealAvailabilityEntity) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, meal_availability_id: str) -> Optional[MealAvailabilityEntity]:
        pass

    @abstractmethod
    async def get_by_daily_menu_meal(self, daily_menu_id: str, meal_id: str) -> Optional[MealAvailabilityEntity]:
        pass
    @abstractmethod
    async def get_by_daily_menu(self, daily_menu_id: str) -> list[MealAvailabilityEntity]:
        pass
    @abstractmethod
    async def reserve_quantity(self, meal_availability_id: str, quantity: int) -> str:
        pass
    @abstractmethod
    async def release_quantity(self, meal_availability_id: str, quantity: int) -> str:
        pass
    @abstractmethod
    async def get_available_quantity(self, meal_availability_id: str) -> int:
        pass
    @abstractmethod
    async def update(self, meal_availability: MealAvailabilityEntity) -> str:
        pass