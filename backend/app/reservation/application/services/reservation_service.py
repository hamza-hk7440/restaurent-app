from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

class IReservationService(ABC):
    @abstractmethod
    async def create_reservation(self, student_id: str, restaurent_id: str, date: datetime, time_slot: str, total_price: float, confirmation_number: str, qr_code_path: str):
        pass
    @abstractmethod
    async def modify_reservation(self, reservation_id: str, date: Optional[datetime] = None, time_slot: Optional[str] = None, total_price: Optional[float] = None):
        pass
    @abstractmethod
    async def cancel_reservation(self, reservation_id: str):
        pass
    @abstractmethod
    async def validate_can_modify(self, reservation_id: str) -> bool:
        pass
    @abstractmethod
    async def validate_can_cancel(self, reservation_id: str) -> bool:
        pass
    @abstractmethod
    async def calculate_total_price(self, restaurent_id: str, date: datetime, time_slot: str) -> float:
        pass