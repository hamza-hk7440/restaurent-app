from typing import List, Tuple
from uuid import UUID

from reservation.domain.entities.notification_entity import Notification
from reservation.domain.interfaces.notification_repo import INotificationRepository
from reservation.application.dtos.payment_and_notification_dtos import (
    GetStudentNotificationsQuery,
    NotificationResponseDTO,
    PaginatedNotificationsResponseDTO,
)
class GetStudentNotificationsUseCase:
    def __init__(self, notification_repository: INotificationRepository):
        self._notification_repo = notification_repository

    async def execute(
        self, query: GetStudentNotificationsQuery
    ) -> PaginatedNotificationsResponseDTO:
        notifications, total_count = await self._fetch_notifications_and_count(query)
        dtos = self._map_to_response_dtos(notifications)
        return self._build_paginated_response(
            dtos=dtos,
            total=total_count,
            limit=query.limit,
            offset=query.offset,
        )

    async def _fetch_notifications_and_count(
        self, query: GetStudentNotificationsQuery
    ) -> Tuple[List[Notification], int]:
        notifications = await self._notification_repo.get_by_student_id(
            student_id=query.student_id,
            limit=query.limit,
            offset=query.offset,
            status=query.status,
        )
        total_count = await self._notification_repo.count_by_student_id(
            student_id=query.student_id,
            status=query.status,
        )
        return notifications, total_count

    @staticmethod
    def _map_to_response_dtos(
        notifications: List[Notification],
    ) -> List[NotificationResponseDTO]:
        return [NotificationResponseDTO.from_entity(item) for item in notifications]

    @staticmethod
    def _build_paginated_response(
        dtos: List[NotificationResponseDTO], total: int, limit: int, offset: int
    ) -> PaginatedNotificationsResponseDTO:
        return PaginatedNotificationsResponseDTO(
            items=dtos,
            total=total,
            limit=limit,
            offset=offset,
        )