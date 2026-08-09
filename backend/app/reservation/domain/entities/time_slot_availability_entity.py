from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException

class TimeSlotAvailabilityEntity:
    id: UUID
    time_slot_id: UUID
    date: datetime
    quantity_available: int
    quantity_reserved: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, time_slot_id: UUID, date: datetime, quantity_available: int, quantity_reserved: int) -> 'TimeSlotAvailabilityEntity':
        if not time_slot_id or not date or quantity_available is None or quantity_reserved is None:
            raise InvalidEntityException("All fields are required to create a TimeSlotAvailabilityEntity.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            time_slot_id=time_slot_id,
            date=date,
            quantity_available=quantity_available,
            quantity_reserved=quantity_reserved,
            created_at=now,
            updated_at=now
        )