from uuid import UUID
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from typing import List
import json
from user_management.presentation.dependencies import get_admin_controller
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
