from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class PunishmentDTO(BaseModel):
    reason: Annotated[str, Field(description="The reason for the punishment.")]
    duration: Annotated[int, Field(description="The duration of the punishment in days.")]
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reason": "Making a problem in the restaurant",
                "duration": 30
            }
        }
    )