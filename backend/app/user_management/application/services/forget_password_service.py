from abc import ABC, abstractmethod

class IForgetPasswordService(ABC):
    @abstractmethod
    async def request_reset(self, email: str) -> None:
        pass
    @abstractmethod
    async def reset_password(self,token: str, new_password: str) -> None:
        pass