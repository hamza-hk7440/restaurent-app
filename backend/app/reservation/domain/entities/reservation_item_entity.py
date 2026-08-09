from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException

class ReservationItemEntity:
    id: UUID
    reservation_id: UUID
    meal_id: UUID
    quantity: int
    unit_price: float
    subtotal: float
    created_at: datetime

    @classmethod
    def create(cls, reservation_id: UUID, meal_id: UUID, quantity: int, unit_price: float) -> 'ReservationItemEntity':
        if not reservation_id or not meal_id or quantity is None or unit_price is None:
            raise InvalidEntityException("All fields are required to create a ReservationItemEntity.")
        subtotal = quantity * unit_price
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            reservation_id=reservation_id,
            meal_id=meal_id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            created_at=now
        )