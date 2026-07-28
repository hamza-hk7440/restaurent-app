from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from user_management.domain.value_objects.token_type import TokenType

class TokenSchema(BaseModel):
    token_id: UUID = Field(..., description="The unique identifier of the token.")
    user_id: UUID = Field(..., description="The unique identifier of the user associated with the token.")
    token_type: TokenType = Field(..., description="The type of the token (e.g., verification, password reset).")
    token_value: str = Field(..., description="The value of the token.")
    created_at: datetime = Field(..., description="The timestamp when the token was created.")
    expires_at: datetime = Field(..., description="The timestamp when the token will expire.")

    class Config:
        from_attributes = True
        use_enum_values = True