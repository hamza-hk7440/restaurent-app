from fastapi import HTTPException
import traceback

from user_management.presentation.schemas.get_punishment_schema import  GetPunishmentResponseSchema
from user_management.application.use_cases.queries.get_punishments_by_students_id_uc import GetPunishmentsByStudentIdUseCase
class GetPunishmentsController:
    def __init__(self, get_punishments_by_student_id_uc: GetPunishmentsByStudentIdUseCase):
        self.get_punishments_by_student_id_uc = get_punishments_by_student_id_uc

    async def get_punishments(self, student_id: str) -> GetPunishmentResponseSchema:
        try:
            print(f"[debug][get_punishments][controller] request student_id={student_id}")
            punishments = await self.get_punishments_by_student_id_uc.get_punishments(student_id=student_id)
            print("[debug][get_punishments][controller] success")
            return GetPunishmentResponseSchema(punishments=[punishment.__dict__ for punishment in punishments])
        except Exception as e:
            print("[debug][get_punishments][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))