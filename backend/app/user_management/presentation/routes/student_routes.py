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
@student_router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    student_id: str,
    old_password: str,
    new_password: str,
    student_controller: StudentController = Depends(get_student_controller)
):
    result = await student_controller.change_password(student_id, old_password, new_password)
    return {"message": result}
@student_router.post("/change-email", status_code=status.HTTP_200_OK)
async def change_email(
    student_id: str,
    current_password: str,
    new_email: str,
    student_controller: StudentController = Depends(get_student_controller)
):
    result = await student_controller.change_email(student_id, current_password, new_email)
    return {"message": result}
@student_router.get("/profile-info", status_code=status.HTTP_200_OK)
async def display_profile_info(
    student_id: str,
    student_controller: StudentController = Depends(get_student_controller)
):
    result = await student_controller.display_profile_info(student_id)
    return {"profile_info": result}
@student_router.get("/all-students", status_code=status.HTTP_200_OK)
async def get_all_students(
    student_controller: StudentController = Depends(get_student_controller)
):
    result = await student_controller.get_all_students()
    return {"students": result}