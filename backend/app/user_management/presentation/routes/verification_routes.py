from fastapi import APIRouter, Depends, status
from user_management.presentation.dependencies import get_verify_email_controller, get_forget_password_controller
from user_management.presentation.controllers.verify_email_controller import VerifyEmailController
from user_management.presentation.controllers.forget_password_controller import ForgetPasswordController
from user_management.presentation.schemas.password_reset_schema import ForgetPasswordRequestSchema, ResetPasswordRequestSchema

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    controller: VerifyEmailController = Depends(get_verify_email_controller)
):
    return await controller.verify_email(token)
@router.get("/verify-email-change", status_code=status.HTTP_200_OK)
async def verify_email_change(
    token: str,
    controller: VerifyEmailController = Depends(get_verify_email_controller)
):
    return await controller.verify_email_for_change(token)
@router.post("/forget-password", status_code=status.HTTP_200_OK)
async def forget_password(
    payload: ForgetPasswordRequestSchema,
    controller: ForgetPasswordController = Depends(get_forget_password_controller)
):
    return await controller.request_reset(payload.email)

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    payload: ResetPasswordRequestSchema,
    controller: ForgetPasswordController = Depends(get_forget_password_controller)
):
    return await controller.reset_password(payload.token, payload.new_password)
