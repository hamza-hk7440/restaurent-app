from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException

class DailyMenu:
    id: UUID
    restaurent_id: UUID
    date: datetime
    is_available: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, restaurent_id: UUID, date: datetime, is_available: bool, created_by: UUID) -> 'DailyMenu':
        if not restaurent_id or not date or is_available is None or not created_by:
            raise InvalidEntityException("All fields are required to create a DailyMenu.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            restaurent_id=restaurent_id,
            date=date,
            is_available=is_available,
            created_by=created_by,
            created_at=now,
            updated_at=now
        )