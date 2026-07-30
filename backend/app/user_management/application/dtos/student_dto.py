from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

class StudentDTO(BaseModel):
    first_name: Annotated[str, Field(description="The first name of the student.")]
    last_name: Annotated[str, Field(description="The last name of the student.")]
    email: Annotated[str, Field(description="The email address of the student.")]
    registration_number: Annotated[str, Field(description="The registration number of the student.")]
    email_verified: Annotated[bool, Field(description="Indicates whether the student's email is verified.")]
    establishment: Annotated[str, Field(description="The establishment associated with the student.")]
    email_verified_at: Annotated[datetime | None, Field(description="The timestamp when the student's email was verified, if applicable.")]
    balance: Annotated[int, Field(description="The balance associated with the student.")]
    status: Annotated[str, Field(description="The status of the student.")]
    updated_at: Annotated[datetime, Field(description="The timestamp when the student's information was last updated.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                
            }
        }
    )
    @classmethod
    def from_entity(cls, student) -> 'StudentDTO':
        return cls(
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            registration_number=student.registration_number,
            email_verified=student.email_verified,
            establishment=student.establishment,
            email_verified_at=student.email_verified_at,
            balance=student.balance,
            status=student.status,
            updated_at=student.updated_at
        )