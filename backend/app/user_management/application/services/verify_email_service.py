from abc import ABC, abstractmethod

class IVerifyEmailService(ABC):
    @abstractmethod
    async def verify_email(self, token: str) -> bool:
        pass
    @abstractmethod
    async def verify_email_for_change(self, token: str) -> bool:
        pass