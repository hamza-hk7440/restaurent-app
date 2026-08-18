from datetime import date, datetime, timezone
from typing import List, Tuple, Optional
from uuid import uuid4

from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.entities.notification_entity import Notification
from reservation.domain.value_objects.notification_type import NotificationType
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.interfaces.notification_repo import INotificationRepository
from reservation.application.services.notification_service import INotificationService
 
from reservation.application.dtos.payment_and_notification_dtos import (
    NotificationResponseDTO,
    SendScheduledRemindersCommand,
    SendScheduledRemindersResponseDTO,
)

class SendScheduledRemindersUseCase:
    def __init__(
        self,
        reservation_repository: IReservationRepository,
        notification_repository: INotificationRepository,
        notification_service: INotificationService,
    ):
        self._reservation_repo = reservation_repository
        self._notification_repo = notification_repository
        self._notification_service = notification_service

    async def execute(
        self, command: SendScheduledRemindersCommand
    ) -> SendScheduledRemindersResponseDTO:
        target_date = command.target_date or date.today()
        eligible_reservations = await self._reservation_repo.get_pending_reminders(
            target_date=target_date, limit=command.limit
        )

        results = [
            await self._process_single_reminder(res) for res in eligible_reservations
        ]

        return self._build_batch_response(results)

    async def _process_single_reminder(
        self, reservation: Reservation
    ) -> Tuple[NotificationResponseDTO, bool]:
        notification_entity = self._build_reminder_entity(reservation)
        dispatch_success = await self._dispatch_notification(notification_entity)

        notification_entity.status = (
            NotificationStatus.SENT if dispatch_success else NotificationStatus.FAILED
        )
        notification_entity.sent_at = datetime.now(timezone.utc)

        saved_notification = await self._notification_repo.save(notification_entity)
        await self._reservation_repo.mark_reminder_sent(reservation.id)

        dto = NotificationResponseDTO.from_entity(saved_notification)
        return dto, dispatch_success

    @staticmethod
    def _build_reminder_entity(reservation: Reservation) -> Notification:
        return Notification(
            id=uuid4(),
            student_id=reservation.student_id,
            reservation_id=reservation.id,
            notification_type=NotificationType.REMINDER,
            title="Reservation Reminder",
            message=(
                f"Reminder: You have an active meal reservation scheduled for "
                f"{reservation.date}. Please present your QR code at redemption time."
            ),
            status=NotificationStatus.PENDING,
            sent_at=datetime.now(timezone.utc),
        )

    async def _dispatch_notification(self, notification: Notification) -> bool:
        try:
            return await self._notification_service.send(notification)
        except Exception:
            return False

    @staticmethod
    def _build_batch_response(
        results: List[Tuple[NotificationResponseDTO, bool]]
    ) -> SendScheduledRemindersResponseDTO:
        notifications = [dto for dto, _ in results]
        success_count = sum(1 for _, is_success in results if is_success)
        failed_count = len(results) - success_count

        return SendScheduledRemindersResponseDTO(
            total_processed=len(results),
            successful_sent=success_count,
            failed_sent=failed_count,
            notifications=notifications,
        )