from user_management.domain.exceptions.domain_exception import InvalidEntityException
from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4
from user_management.domain.value_objects.token_type import TokenType

@dataclass(frozen=True)
class Token:
    token_id: UUID
    user_id: UUID
    token_type: TokenType
    token_value: str
    created_at: datetime
    expires_at: datetime

    @classmethod
    def create(cls, user_id: UUID, token_type: TokenType, token_value: str, expires_at: datetime) -> 'Token':
        if not user_id or not token_type or not token_value or not expires_at:
            raise InvalidEntityException("All fields are required to create a Token.")
        now = datetime.now(timezone.utc)
        return cls(
            token_id=uuid4(),
            user_id=user_id,
            token_type=token_type,
            token_value=token_value,
            created_at=now,
            expires_at=expires_at
        )