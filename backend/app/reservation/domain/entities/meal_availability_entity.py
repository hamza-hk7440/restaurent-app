from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException

class MealAvailabilityEntity:
    id: UUID
    daily_menu_id: UUID
    quantity_available: int
    quantity_reserved: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, daily_menu_id: UUID, quantity_available: int, quantity_reserved: int) -> 'MealAvailabilityEntity':
        if not daily_menu_id or quantity_available is None or quantity_reserved is None:
            raise InvalidEntityException("All fields are required to create a MealAvailabilityEntity.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            daily_menu_id=daily_menu_id,
            quantity_available=quantity_available,
            quantity_reserved=quantity_reserved,
            created_at=now,
            updated_at=now
        )