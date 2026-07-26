from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class StudentDTO(BaseModel):
    first_name: Annotated[str, Field(description="The first name of the student.")]
    last_name: Annotated[str, Field(description="The last name of the student.")]
    email: Annotated[str, Field(description="The email address of the student.")]
    
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
            email=student.email
        )