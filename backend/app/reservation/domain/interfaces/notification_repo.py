from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from reservation.domain.interfaces.base import IRepository
from reservation.domain.entities.notification_entity import Notification
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.value_objects.notification_type import NotificationType
class INotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification: Notification) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        pass

    @abstractmethod
    async def get_by_reservation(self, reservation_id: str) -> list[Notification]:
        pass
    @abstractmethod
    async def get_pending_notifications(self) -> list[Notification]:
        pass
    @abstractmethod
    async def get_by_student(self, student_id: str) -> list[Notification]:
        pass
    @abstractmethod
    async def get_by_type(self, notification_type: NotificationType) -> list[Notification]:
        pass
    @abstractmethod
    async def update_status(self, notification_id: str, status: NotificationStatus) -> str:
        pass
    @abstractmethod
    async def mark_sent(self, notification_id: str) -> str:
        pass
    @abstractmethod
    async def mark_read(self, notification_id: str) -> str:
        pass
    @abstractmethod
    async def update(self, notification: Notification) -> str:
        pass