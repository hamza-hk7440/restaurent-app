from pydantic import BaseModel, Field


class GetPunishmentResponseSchema(BaseModel):
    punishments: list[dict] = Field(..., description="A list of punishments associated with the student.")