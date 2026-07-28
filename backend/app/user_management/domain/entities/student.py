from user_management.domain.exceptions.domain_exception import InvalidEntityException
from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4
from user_management.domain.value_objects.status import StudentStatus
@dataclass(frozen=True)
class Student:
    student_id: UUID
    first_name: str
    last_name: str
    email: str
    password:str
    created_at: datetime
    updated_at: datetime
    establishment:str
    registration_number:str
    status: StudentStatus 
    email_verified: bool = False
    email_verified_at: datetime = None
    balance: int = 0
    @classmethod
    def create(cls, first_name: str, last_name: str, email: str, password:str, establishment:str, registration_number:str, status: StudentStatus) -> 'Student':
        if not first_name or not last_name or not email or not password or not establishment or not registration_number:
            raise InvalidEntityException("All fields are required to create a Student.")
        now = datetime.now(timezone.utc)
        return cls(
            student_id=uuid4(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            created_at=now,
            updated_at=now,
            establishment=establishment,
            registration_number=registration_number,
            status=status,
            email_verified=False,
            email_verified_at=None
            
        )
