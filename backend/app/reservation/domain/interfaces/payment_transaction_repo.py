from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from reservation.domain.entities.transaction_entity import Transaction


class IPaymentTransactionRepository(ABC):
    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        """Saves or updates a payment transaction entity."""
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Retrieves a payment transaction by its UUID."""
        pass

    @abstractmethod
    async def get_by_reservation_id(self, reservation_id: UUID) -> List[Transaction]:
        """Retrieves all payment transactions linked to a reservation."""
        pass

    @abstractmethod
    async def get_by_student_id(self, student_id: UUID) -> List[Transaction]:
        """Retrieves all payment transactions owned by a student."""
        pass