from fastapi import HTTPException
import traceback

from user_management.presentation.schemas.admin_schema import AdminSchema

from user_management.application.use_cases.commands.create_student_uc import CreateStudentUseCase

class AdminController:
    def __init__(self, create_student_uc: CreateStudentUseCase):
        self.create_student_uc = create_student_uc

    async def create_student(self, first_name: str, last_name: str, email: str, registration_number: str, establishment: str) -> str:
        try:
            print(f"[debug][create_student][controller] request email={email} registration_number={registration_number} establishment={establishment}")
            token = await self.create_student_uc.create_student(first_name, last_name, email, registration_number, establishment)
            print("[debug][create_student][controller] success")
            return token
        except Exception as e:
            print("[debug][create_student][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    