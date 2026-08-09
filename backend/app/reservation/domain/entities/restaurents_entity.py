from dataclasses import dataclass
from datetime import datetime, timezone,time
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException
from reservation.domain.value_objects.restaurent_status import RestaurantStatus
@dataclass(frozen=True)
class Restaurent:
    id: UUID
    name: str
    establishments_id:UUID
    address: str
    phone: str
    openining_time: time
    closing_time: time
    status: RestaurantStatus
    created_at: datetime
    updated_at: datetime
    @classmethod
    def create(cls, name: str, establishments_id:UUID,address: str, phone: str, openining_time: time, closing_time: time, status: RestaurantStatus) -> 'Restaurant':
        if not name or not establishments_id or not address or not phone or not openining_time or not closing_time or not status:
            raise InvalidEntityException("All fields are required to create a Restaurant.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            name=name,
            establishments_id=establishments_id,
            address=address,
            phone=phone,
            openining_time=openining_time,
            closing_time=closing_time,
            status=status,
            created_at=now,
            updated_at=now
        )