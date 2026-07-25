from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel,Field,ConfigDict

class AdminDTO(BaseModel):
    admin_id: Annotated[UUID, Field(description="The unique identifier of the admin.")]
    username: Annotated[str, Field(description="The username of the admin.")]
    email: Annotated[str, Field(description="The email address of the admin.")]
    created_at: Annotated[datetime, Field(description="The timestamp when the admin was created.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "admin_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "admin_user",
                "email": "admin@example.com",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
    )