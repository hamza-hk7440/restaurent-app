from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.meals_entity import Meal
from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.meal_category import MealCategory

class IMealRepository(ABC):
    @abstractmethod
    async def create(self, meal: Meal) -> str:
        pass
    @abstractmethod
    async def get_by_id(self, meal_id: str) -> Optional[Meal]:
        pass
    @abstractmethod
    async def get_by_code(self, meal_code: str) -> Optional[Meal]:
        pass
    @abstractmethod
    async def get_by_category(self, category: MealCategory) -> list[Meal]:
        pass
    @abstractmethod
    async def get_by_restaurent(self, restaurent_id: str) -> list[Meal]:
        pass
    @abstractmethod
    async def search_by_name(self, name: str) -> list[Meal]:
        pass
    @abstractmethod
    async def get_available_meals(self) -> list[Meal]:
        pass
    @abstractmethod
    async def get_by_rating(self, min_rating: float) -> list[Meal]:
        pass
    @abstractmethod
    async def get_by_popularity(self, min_popularity: float) -> list[Meal]:
        pass
    @abstractmethod
    async def update(self, meal: Meal) -> str:
        pass
    @abstractmethod
    async def delete(self, meal_id: str) -> str:
        pass
    @abstractmethod
    async def update_availability(self, meal_id: str, availability_status: MealAvailability) -> str:
        pass