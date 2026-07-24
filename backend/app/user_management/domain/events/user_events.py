from dataclasses import dataclass
from uuid import UUID
from user_management.domain.interfaces.base import DomainEvent
from datetime import datetime, timezone

@dataclass(frozen=True)
class StudentCreatedEvent(DomainEvent):
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    establishment: str
    registration_number: str
    created_at: datetime = datetime.now(timezone.utc)
@dataclass(frozen=True)
class PasswordChangedEvent(DomainEvent):
    user_id: UUID
    changed_at: datetime = datetime.now(timezone.utc)
@dataclass(frozen=True)
class UserDeletedEvent(DomainEvent):
    user_id: UUID
    deleted_at: datetime = datetime.now(timezone.utc)
    