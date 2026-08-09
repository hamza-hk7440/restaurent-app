from abc import ABC, abstractmethod
class INotificationService(ABC):
    @abstractmethod
    async def send_reminder_24h(self, reservation_id: str) -> str:
        pass
    @abstractmethod
    async def send_reminder_1h(self, reservation_id: str) -> str:
        pass
    @abstractmethod
    async def send_confirmation(self, reservation_id: str) -> str:
        pass
    @abstractmethod
    async def send_cancellation(self, reservation_id: str) -> str:
        pass
    @abstractmethod
    async def send_modification(self, reservation_id: str) -> str:
        pass