from typing import Optional
from uuid import UUID

from reservation.domain.entities.notification_entity import Notification
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.interfaces.notification_repo import INotificationRepository
from reservation.domain.exceptions.domain_exceptions import (
    NotificationNotFoundException,
    InvalidNotificationStateException,
)

from reservation.application.dtos.payment_and_notification_dtos import (MarkNotificationReadCommand,NotificationResponseDTO)


class MarkNotificationReadUseCase:
    def __init__(self, notification_repository: INotificationRepository):
        self._notification_repo = notification_repository

    async def execute(
        self, command: MarkNotificationReadCommand
    ) -> NotificationResponseDTO:
        notification = await self._get_notification_or_raise(command.notification_id)

        self._verify_ownership_if_provided(notification, command.student_id)
        self._verify_can_be_marked_read(notification)

        updated_notification = await self._apply_read_status(notification)

        return NotificationResponseDTO.from_entity(updated_notification)

    async def _get_notification_or_raise(self, notification_id: UUID) -> Notification:
        notification = await self._notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(
                f"Notification with ID '{notification_id}' not found."
            )
        return notification

    @staticmethod
    def _verify_ownership_if_provided(
        notification: Notification, student_id: Optional[UUID]
    ) -> None:
        if student_id and str(notification.student_id) != str(student_id):
            raise InvalidNotificationStateException(
                f"Notification '{notification.id}' does not belong to student '{student_id}'."
            )

    @staticmethod
    def _verify_can_be_marked_read(notification: Notification) -> None:
        status_val = (
            notification.status.value
            if hasattr(notification.status, "value")
            else str(notification.status)
        )

        read_val = (
            NotificationStatus.READ.value
            if hasattr(NotificationStatus, "READ")
            else "read"
        )

        if status_val == read_val:
            raise InvalidNotificationStateException(
                f"Notification '{notification.id}' is already marked as read."
            )

    async def _apply_read_status(
        self, notification: Notification
    ) -> Notification:
        read_status = getattr(NotificationStatus, "READ", NotificationStatus.SENT)
        notification.status = read_status
        return await self._notification_repo.update_status(notification.id, read_status)