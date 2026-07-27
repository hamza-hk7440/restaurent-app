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

