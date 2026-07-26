from user_management.domain.exceptions.domain_exception import InvalidEntityException
from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4

@dataclass(frozen=True)
class Punishment:
    punishment_id: UUID
    student_id: UUID
    admin_id: UUID
    reason: str
    period_of_ban: str
    created_at: datetime
    @classmethod
    def create(cls, student_id: UUID, admin_id: UUID, reason: str, period_of_ban: str) -> 'Punishment':
        if not student_id or not admin_id or not reason or not period_of_ban:
            raise InvalidEntityException("All fields are required to create a Punishment.")
        now = datetime.now(timezone.utc)
        return cls(
            punishment_id=uuid4(),
            student_id=student_id,
            admin_id=admin_id,
            reason=reason,
            period_of_ban=period_of_ban,
            created_at=now
        )