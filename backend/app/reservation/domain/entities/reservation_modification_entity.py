from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException
from reservation.domain.value_objects.reservation_modification_type import ReservationModificationType

class ReservationModificationEntity:
    id: UUID
    reservation_id: UUID
    modification_type: ReservationModificationType
    old_value: str
    new_value: str
    price_adjustment: float
    created_at: datetime

    @classmethod
    def create(cls, reservation_id: UUID, modification_type: ReservationModificationType, old_value: str, new_value: str, price_adjustment: float) -> 'ReservationModificationEntity':
        if not reservation_id or not modification_type or old_value is None or new_value is None or price_adjustment is None:
            raise InvalidEntityException("All fields are required to create a ReservationModificationEntity.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            reservation_id=reservation_id,
            modification_type=modification_type,
            old_value=old_value,
            new_value=new_value,
            price_adjustment=price_adjustment,
            created_at=now
        )