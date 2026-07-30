from uuid import UUID
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from typing import List
import json
from user_management.presentation.dependencies import get_get_punishments_by_student_id_controller
from user_management.presentation.controllers.get_punishments_controller import GetPunishmentsController
from user_management.presentation.schemas.get_punishment_schema import GetPunishmentResponseSchema
from user_management.application.dtos.punishment_dto import PunishmentDTO

get_punishment_router = APIRouter(prefix="/punishments", tags=["Punishments"])

@get_punishment_router.post("/get_punishments_by_student_id", response_model=List[PunishmentDTO], status_code=status.HTTP_200_OK)
async def get_punishments_by_student_id(
    student_id: str,
    get_punishments_controller: GetPunishmentsController = Depends(get_get_punishments_by_student_id_controller)
):
    return await get_punishments_controller.get_punishments(student_id=student_id)