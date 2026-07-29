from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class PunishmentSchema(BaseModel):
    punishment_id: UUID = Field(..., description="The unique identifier of the punishment.")
    student_id: UUID = Field(..., description="The unique identifier of the student.")
    admin_id: UUID = Field(..., description="The unique identifier of the admin who issued the punishment.")
    reason: str = Field(..., description="The reason for the punishment.")
    period_of_ban: int = Field(..., description="The duration of the ban.")
    created_at: datetime = Field(..., description="The timestamp when the punishment was created.")

    class Config:
        from_attributes = True

        