from dataclasses import dataclass
from uuid import UUID
from user_management.domain.interfaces.base import DomainEvent
from datetime import datetime, timezone

@dataclass(frozen=True)
class StudentCreatedEvent(DomainEvent):
    student_id: UUID
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
class EmailChangedEvent(DomainEvent):
    user_id: UUID
    new_email: str
    changed_at: datetime = datetime.now(timezone.utc)
@dataclass(frozen=True)
class StudentInfoEditedEvent(DomainEvent):
    user_id: UUID
    new_first_name: str
    new_last_name: str
    edited_at: datetime = datetime.now(timezone.utc)
@dataclass(frozen=True)
class BannedStudentEvent(DomainEvent):
    user_id: UUID
    period_of_ban: str
    banned_at: datetime = datetime.now(timezone.utc)
    
@dataclass(frozen=True)
class UnbannedStudentEvent(DomainEvent):
    user_id: UUID
    unbanned_at: datetime = datetime.now(timezone.utc)
@dataclass(frozen=True)
class DesactivatedStudentEvent(DomainEvent):
    user_id: UUID
    desactivated_at: datetime = datetime.now(timezone.utc)
@dataclass(frozen=True)
class ReactivatedStudentEvent(DomainEvent):
    user_id: UUID
    reactivated_at: datetime = datetime.now(timezone.utc)
    