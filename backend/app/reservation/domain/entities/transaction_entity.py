from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException
from reservation.domain.value_objects.transaction_status import TransactionStatus
from reservation.domain.value_objects.transaction_type import TransactionType

class Transaction:
    id: UUID
    student_id: UUID
    reservation_id: UUID
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus
    payment_method: str
    reference_id: str
    created_at: datetime

    @classmethod
    def create(cls, student_id: UUID, reservation_id: UUID, amount: float, transaction_type: TransactionType, payment_method: str, reference_id: str) -> 'Transaction':
        if not student_id or not reservation_id or amount is None or not transaction_type or not payment_method or not reference_id:
            raise InvalidEntityException("All fields are required to create a Transaction.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            student_id=student_id,
            reservation_id=reservation_id,
            amount=amount,
            transaction_type=transaction_type,
            status=TransactionStatus.PENDING,
            payment_method=payment_method,
            reference_id=reference_id,
            created_at=now
        )