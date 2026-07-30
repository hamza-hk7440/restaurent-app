from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class PunishmentDTO(BaseModel):
    student_id: Annotated[str, Field(description="The ID of the student to be punished.")]
    reason: Annotated[str, Field(description="The reason for the punishment.")]
    period_of_ban: Annotated[int, Field(description="The duration of the punishment in days.")]
    admin_id: Annotated[str, Field(description="The ID of the admin who issued the punishment.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reason": "Making a problem in the restaurant",
                "period_of_ban": 30
            }
        }
    )
    @classmethod
    def from_entity(cls, punishment) -> 'PunishmentDTO':
        return cls(
            student_id=str(punishment.student_id),
            reason=punishment.reason,
            period_of_ban=punishment.period_of_ban,
            admin_id=str(punishment.admin_id)
        )