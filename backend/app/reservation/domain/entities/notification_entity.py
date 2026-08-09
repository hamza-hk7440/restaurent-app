from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.value_objects.notification_type import NotificationType

class Notification:
    id: UUID
    reservation_id: UUID
    student_id: UUID
    notification_type: NotificationType
    message: str
    status: NotificationStatus
    sent_at: datetime
    created_at: datetime

    @classmethod
    def create(cls, reservation_id: UUID, student_id: UUID, notification_type: NotificationType, message: str) -> 'Notification':
        if not reservation_id or not student_id or not notification_type or not message:
            raise InvalidEntityException("All fields are required to create a Notification.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            reservation_id=reservation_id,
            student_id=student_id,
            notification_type=notification_type,
            message=message,
            status=NotificationStatus.PENDING,
            sent_at=None,
            created_at=now
        )