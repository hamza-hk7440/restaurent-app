from user_management.domain.exceptions.domain_exception import InvalidEntityException

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

@dataclass(frozen=True)
class Admin:
    admin_id: UUID
    username: str
    email: str
    password: str
    created_at: datetime
    @classmethod
    def create(cls, username: str, email: str, password: str) -> 'Admin':
        if not username or not email or not password:
            raise InvalidEntityException("All fields are required to create an Admin.")
        now = datetime.now(timezone.utc)
        return cls(
            admin_id=uuid4(),
            username=username,
            email=email,
            password=password,
            created_at=now
        )