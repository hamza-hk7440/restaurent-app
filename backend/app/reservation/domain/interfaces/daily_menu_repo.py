from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.daily_menu_entity import DailyMenu

class IDailyMenuRepository(ABC):
    @abstractmethod
    async def create(self, daily_menu: DailyMenu) -> str:
        pass
    @abstractmethod
    async def get_by_id(self, daily_menu_id: str) -> Optional[DailyMenu]:
        pass
    @abstractmethod
    async def get_by_restaurent_and_date_range(self, restaurent_id: str, start_date: datetime, end_date: datetime) -> List[DailyMenu]:
        pass
    @abstractmethod
    async def get_by_restaurent_by_date(self, restaurent_id: str, date: datetime) -> Optional[DailyMenu]:
        pass
    @abstractmethod
    async def update(self, daily_menu: DailyMenu) -> str:
        pass
    @abstractmethod
    async def delete(self, daily_menu_id: str) -> str:
        pass
    @abstractmethod
    async def mark_as_available(self, daily_menu_id: str) -> str:
        pass
    @abstractmethod
    async def mark_as_unavailable(self, daily_menu_id: str) -> str:
        pass
    
