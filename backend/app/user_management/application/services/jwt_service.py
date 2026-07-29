from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from user_management.domain.value_objects.token_type import TokenType

class IJWTService(ABC):
    @abstractmethod
    def generate_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) ->Optional[str]:
        pass
    @abstractmethod
    def generate_verification_token() -> str:
        pass
    @abstractmethod
    def generate_password_reset_token() -> str:
        pass
    @abstractmethod
    def is_token_expired(self, expires_at: datetime) -> bool:
        pass
    @abstractmethod
    async def save_token(self, user_id: str, token: str, expires_at: datetime, token_type: TokenType = TokenType.REFRESH) -> None:
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
    @abstractmethod
    async def get_token_expiry_time():
        pass
    @abstractmethod
    async def save_verification_token(self, user_id: str, token: str, expires_at: datetime, token_type: TokenType = TokenType.VERIFICATION) -> Optional[str]:
        pass
