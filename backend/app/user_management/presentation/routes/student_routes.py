from fastapi import APIRouter, Depends, status
from user_management.presentation.dependencies import get_student_controller
from user_management.presentation.controllers.student_controller import StudentController

student_router = APIRouter(prefix="/students", tags=["Students"])
@student_router.post("/normal-login", status_code=status.HTTP_200_OK)
async def normal_login(
    email: str,
    password: str,
    student_controller: StudentController = Depends(get_student_controller)
):
    token = await student_controller.normal_login(email, password)
    return {"token": token}
