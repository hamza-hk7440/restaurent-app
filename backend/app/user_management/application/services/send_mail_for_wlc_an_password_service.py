from abc import ABC, abstractmethod

class ISendMailForWlcAndPasswordService(ABC):
    @abstractmethod
    async def send_welcome_email(self,receiver_mail:str, password: str) -> None:
        pass
    @abstractmethod
    async def send_password_reset_email(self,receiver_mail:str, password: str) -> None:
        pass
    @abstractmethod
    async def send_verification_email(self,receiver_mail:str) -> str:
        pass
    