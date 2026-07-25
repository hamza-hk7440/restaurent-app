from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

class IJWTService(ABC):
    @abstractmethod
    def generate_token(self, user_id: str,expires_delta:Optional[timedelta]) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) ->Optional[str]:
        pass