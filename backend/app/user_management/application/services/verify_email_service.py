from abc import ABC, abstractmethod

class IVerifyEmailService(ABC):
    @abstractmethod
    async def verify_email(self, token: str) -> bool:
        pass