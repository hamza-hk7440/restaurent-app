from fastapi import APIRouter, Depends, status
from user_management.presentation.dependencies import get_verify_email_controller
from user_management.presentation.controllers.verify_email_controller import VerifyEmailController

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    controller: VerifyEmailController = Depends(get_verify_email_controller)
):
    return await controller.verify_email(token)