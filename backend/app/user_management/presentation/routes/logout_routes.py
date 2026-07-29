from fastapi import APIRouter, Depends, status
from user_management.presentation.dependencies import get_logout_controller
from user_management.presentation.controllers.logout_controller import LogoutController

logout_router= APIRouter(prefix="/auth", tags=["Auth"])
@logout_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str,
    controller: LogoutController = Depends(get_logout_controller)
):
    return await controller.logout(token)