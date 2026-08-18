from dataclasses import dataclass
from datetime import datetime, timezone,time
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException

class TimeSlotEntity:
    id: UUID
    restaurant_id: UUID
    start_time: time
    end_time: time
    capacity: int
    created_at: datetime
    
    @classmethod
    def create(cls, restaurant_id: UUID, start_time: time, end_time: time, capacity: int) -> 'TimeSlotEntity':
        if not restaurant_id or not start_time or not end_time or capacity is None:
            raise InvalidEntityException("All fields are required to create a TimeSlotEntity.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            restaurant_id=restaurant_id,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
            created_at=now
        )