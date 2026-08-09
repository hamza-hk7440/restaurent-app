from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.value_objects.reservation_status import ReservationStatus
class IReservationRepository(ABC):
    @abstractmethod
    async def create(self, reservation: Reservation) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        pass

    @abstractmethod
    async def get_by_confirmation_number(self, confirmation_number: str) -> Optional[Reservation]:
        pass
    @abstractmethod
    async def get_by_student_id(self, student_id: str) -> list[Reservation]:
        pass
    @abstractmethod
    async def get_upcoming_reservations(self, student_id: str) -> list[Reservation]:
        pass
    @abstractmethod
    async def get_reservation_history(self, student_id: str) -> list[Reservation]:
        pass
    @abstractmethod
    async def get_by_restaurent(self, restaurent_id: str) -> list[Reservation]:
        pass
    @abstractmethod
    async def get_by_restaurent_slot(self, restaurent_id: str, date: datetime, time_slot: str) -> list[Reservation]:
        pass
    @abstractmethod
    async def update(self, reservation: Reservation) -> str:
        pass
    @abstractmethod
    async def update_status(self, reservation_id: str, status: ReservationStatus) -> str:
        pass
    @abstractmethod
    async def cancel(self, reservation_id: str) -> str:
        pass
    @abstractmethod
    async def mark_completed(self, reservation_id: str) -> str:
        pass
    @abstractmethod
    async def check_double_booking(self, student_id: str, date: datetime, time_slot: str) -> bool:
        pass