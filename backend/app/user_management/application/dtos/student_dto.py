from datetime import datetime
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class StudentDTO(BaseModel):
    student_id: Annotated[UUID, Field(description="The unique identifier of the student.")]
    first_name: Annotated[str, Field(description="The first name of the student.")]
    last_name: Annotated[str, Field(description="The last name of the student.")]
    email: Annotated[str, Field(description="The email address of the student.")]
    created_at: Annotated[datetime, Field(description="The timestamp when the student was created.")]
    updated_at: Annotated[datetime, Field(description="The timestamp when the student was last updated.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }
    )
    def from_entity(student) -> 'StudentDTO':
        return StudentDTO(
            student_id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            created_at=student.created_at,
            updated_at=student.updated_at
        )