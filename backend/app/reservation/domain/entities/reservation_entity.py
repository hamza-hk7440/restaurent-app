from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException
from reservation.domain.value_objects.reservation_status import ReservationStatus

class Reservation:
    id: UUID
    student_id: UUID
    restaurent_id: UUID
    date: datetime
    time_slot:UUID
    status: ReservationStatus
    total_price: float
    confirmation_number: str
    qr_code_path: str
    created_at: datetime
    modified_at: datetime
    canceled_at: datetime
    completed_at: datetime
    @classmethod
    def create(cls, student_id: UUID, restaurent_id: UUID, date: datetime, time_slot: UUID, total_price: float, confirmation_number: str, qr_code_path: str) -> "Reservation":
        if not student_id or not restaurent_id or not date or not time_slot or total_price is None or not confirmation_number or not qr_code_path:
            raise InvalidEntityException("All fields are required to create a Reservation.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            student_id=student_id,
            restaurent_id=restaurent_id,
            date=date,
            time_slot=time_slot,
            status=ReservationStatus.CONFIRMED,
            total_price=total_price,
            confirmation_number=confirmation_number,
            qr_code_path=qr_code_path,
            created_at=now,
            modified_at=now,
            canceled_at=None,
            completed_at=None
        )