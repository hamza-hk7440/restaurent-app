from user_management.domain.exceptions.domain_exception import DomainException, InvalidEntityException, EntityNotFoundException, UnauthorizedAccessException, BusinessRuleViolationException

from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4

@dataclass(frozen=True)
class User:
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    password:str
    created_at: datetime
    updated_at: datetime
    establishment:str
    resgistration_number:str
    @classmethod
    def create(cls, first_name: str, last_name: str, email: str, password:str, establishment:str, resgistration_number:str) -> 'User':
        if not first_name or not last_name or not email or not password or not establishment or not resgistration_number:
            raise InvalidEntityException("All fields are required to create a User.")
        now = datetime.now(timezone.utc)
        return cls(
            user_id=uuid4(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            created_at=now,
            updated_at=now,
            establishment=establishment,
            resgistration_number=resgistration_number
        )
