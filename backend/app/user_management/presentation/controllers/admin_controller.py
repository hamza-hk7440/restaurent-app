from fastapi import HTTPException
import traceback

from user_management.presentation.schemas.admin_schema import AdminSchema
from user_management.application.use_cases.commands.change_password_by_admin import ChangePasswordByAdminUseCase
from user_management.application.use_cases.commands.create_student_uc import CreateStudentUseCase
from user_management.application.use_cases.commands.login_for_admin_uc import LoginForAdminUseCase
from user_management.application.use_cases.commands.change_email_by_admin_uc import ChangeEmailByAdminUseCase
from user_management.application.use_cases.commands.ban_student_uc import BanStudentUseCase
class AdminController:
    def __init__(self, create_student_uc: CreateStudentUseCase, login_for_admin_uc: LoginForAdminUseCase, change_password_by_admin_uc: ChangePasswordByAdminUseCase, change_email_by_admin_uc: ChangeEmailByAdminUseCase, ban_student_uc: BanStudentUseCase):
        self.create_student_uc = create_student_uc
        self.login_for_admin_uc = login_for_admin_uc
        self.change_password_by_admin_uc = change_password_by_admin_uc
        self.change_email_by_admin_uc = change_email_by_admin_uc
        self.ban_student_uc = ban_student_uc

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
    async def login_for_admin(self, email: str, password: str) -> str:
        try:
            print(f"[debug][login_for_admin][controller] request email={email}")
            token = await self.login_for_admin_uc.execute(email, password)
            print("[debug][login_for_admin][controller] success")
            return token
        except Exception as e:
            print("[debug][login_for_admin][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def change_password_by_admin(self,student_id) -> str:
        try:
            print(f"[debug][change_password_by_admin][controller] request student_id={student_id}")
            result = await self.change_password_by_admin_uc.change_password_by_admin(student_id)
            print("[debug][change_password_by_admin][controller] success")
            return result
        except Exception as e:
            print("[debug][change_password_by_admin][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def change_email_by_admin(self, student_id: str, new_email: str) -> None:
        try:
            print(f"[debug][change_email_by_admin][controller] request student_id={student_id} new_email={new_email}")
            await self.change_email_by_admin_uc.change_email_by_admin(student_id, new_email)
            print("[debug][change_email_by_admin][controller] success")
        except Exception as e:
            print("[debug][change_email_by_admin][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def ban_student(self, admin_id: str, student_id: str, reason: str, duration: int) -> None:
        try:
            print(f"[debug][ban_student][controller] request admin_id={admin_id} student_id={student_id} reason={reason} duration={duration}")
            await self.ban_student_uc.ban_student(admin_id=admin_id, student_id=student_id, reason=reason, duration=duration)
            print("[debug][ban_student][controller] success")
        except Exception as e:
            print("[debug][ban_student][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
        