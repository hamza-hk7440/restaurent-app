from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class AdminSchema(BaseModel):
    admin_id: UUID = Field(..., description="The unique identifier of the admin.")
    username: str = Field(..., description="The username of the admin.")
    email: str = Field(..., description="The email address of the admin.")
    created_at: datetime = Field(..., description="The timestamp when the admin was created.")

    class Config:
        from_attributes = True