from uuid import UUID
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from typing import List
import json
from user_management.presentation.dependencies import get_admin_controller, require_admin
from user_management.presentation.controllers.admin_controller import AdminController
from user_management.presentation.schemas.admin_schema import AdminSchema

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/create_student", status_code=status.HTTP_201_CREATED)
async def create_student(
    first_name: str,
    last_name: str,
    email: str,
    registration_number: str,
    establishment: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):

    token = await admin_controller.create_student(first_name, last_name, email, registration_number, establishment)
    return {"token": token}
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_admin(
    email: str,
    password: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    token = await admin_controller.login_for_admin(email, password)
    return {"token": token}
@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password_by_admin(
    student_id: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    result = await admin_controller.change_password_by_admin(student_id)
    return {"message": result}

@router.post("/change-email", status_code=status.HTTP_200_OK)
async def change_email_by_admin(
    student_id: str,
    new_email: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.change_email_by_admin(student_id, new_email)
    return {"message": "Email changed successfully"}
@router.post("/ban-student", status_code=status.HTTP_200_OK)
async def ban_student(
    student_id: str,
    reason: str,
    duration: int,
    admin_id: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.ban_student(admin_id=admin_id, student_id=student_id, reason=reason, duration=duration)
    return {"message": "Student banned successfully"}
@router.post("/unban-student", status_code=status.HTTP_200_OK)
async def unban_student(
    student_id: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.unban_student(student_id=student_id)
    return {"message": "Student unbanned successfully"}
@router.post("/activate-student", status_code=status.HTTP_200_OK)
async def activate_student(
    student_id: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.activate_student(student_id=student_id)
    return {"message": "Student activated successfully"}
@router.post("/desactivate-student", status_code=status.HTTP_200_OK)
async def desactivate_student(
    student_id: str,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.desactivate_student(student_id=student_id)
    return {"message": "Student desactivated successfully"}
@router.post("/edit-student-infos", status_code=status.HTTP_200_OK)
async def edit_student_infos(
    student_id: str,
    new_first_name: str = None,
    new_last_name: str = None,
    registration_number: str = None,
    establishment: str = None,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.edit_student_infos(student_id=student_id, new_first_name=new_first_name, new_last_name=new_last_name, registration_number=registration_number, establishment=establishment)
    return {"message": "Student infos edited successfully"}
@router.get("/get-all-admins", status_code=status.HTTP_200_OK, response_model=List[AdminSchema])
async def get_all_admins(
    admin_user: dict = Depends(require_admin),
    admin_controller: AdminController = Depends(get_admin_controller)
):
    admins = await admin_controller.get_all_admins()
    return admins

@router.post("/edit-punishment-period", status_code=status.HTTP_200_OK)
async def edit_punishment_period(
    punishment_id: str,
    new_duration: int,
    admin_controller: AdminController = Depends(get_admin_controller)
):
    await admin_controller.edit_punishment_period(punishment_id=punishment_id, new_duration=new_duration)
    return {"message": "Punishment period edited successfully"}