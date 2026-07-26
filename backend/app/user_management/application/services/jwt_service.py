from abc import ABC, abstractmethod
from datetime import timedelta,datetime
from typing import Optional

class IJWTService(ABC):
    @abstractmethod
    def generate_token(self, user_id: str,expires_delta:Optional[timedelta]) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) ->Optional[str]:
        pass
    @abstractmethod
    def generate_verification_token(self, email: str, expires_delta: Optional[timedelta]) -> str:
        pass
    @abstractmethod
    def generate_password_reset_token(self, email: str, expires_delta: Optional[timedelta]) -> str:
        pass
    @abstractmethod
    def is_token_expired(self, expires_at: datetime) -> bool:
        pass
    @abstractmethod
    async def save_token(self, token: str, expires_at: datetime) -> None:
        pass
    @abstractmethod
    async def verify_verification_token(self, token: str) -> Optional[str]:
        pass
    @abstractmethod
    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        pass
    @abstractmethod
    async def delete_token(self, token: str) -> None:
        pass