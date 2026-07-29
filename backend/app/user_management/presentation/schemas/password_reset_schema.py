from pydantic import BaseModel, Field, EmailStr


class ForgetPasswordRequestSchema(BaseModel):
    email: EmailStr = Field(..., description="The account email to send the reset link to.")


class ResetPasswordRequestSchema(BaseModel):
    token: str = Field(..., description="The password reset token received by email.")
    new_password: str = Field(..., min_length=8, description="The new password.")
