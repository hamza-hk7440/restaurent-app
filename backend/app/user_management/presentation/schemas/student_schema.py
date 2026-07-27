from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from user_management.domain.value_objects.status import StudentStatus

class StudentSchema(BaseModel):
    id: UUID = Field(..., description="The unique identifier of the student.")
    first_name: str = Field(..., description="The first name of the student.")
    last_name: str = Field(..., description="The last name of the student.")
    email: str = Field(..., description="The email address of the student.")
    registration_number: str = Field(..., description="The registration number of the student.")
    establishment: str = Field(..., description="The establishment of the student.")
    status: StudentStatus = Field(..., description="The status of the student.")
    email_verified: bool = Field(..., description="Indicates if the student's email is verified.")
    email_verified_at: datetime | None = Field(None, description="The timestamp when the student's email was verified.")
    balance: int = Field(..., description="The balance of the student.")

    class Config:
        from_attributes = True
        use_enum_values = True
    