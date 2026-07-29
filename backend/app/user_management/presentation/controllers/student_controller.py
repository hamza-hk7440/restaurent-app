from fastapi import HTTPException
import traceback
from user_management.application.use_cases.commands.change_email_by_student_uc import ChangeEmailByStudentUseCase
from user_management.application.use_cases.commands.login_for_students_uc import LoginForStudentsUseCase
from user_management.application.use_cases.commands.change_password_by_student_uc import ChangePasswordByStudentUseCase
from user_management.presentation.controllers.verify_email_controller import VerifyEmailController
from user_management.application.services.jwt_service import IJWTService
class StudentController:
    def __init__(self, login_for_students_uc: LoginForStudentsUseCase, change_password_by_student_uc: ChangePasswordByStudentUseCase, change_email_by_student_uc: ChangeEmailByStudentUseCase, verify_email_controller: VerifyEmailController,jwt_service: IJWTService):
        self.verify_email_controller = verify_email_controller
        self.login_for_students_uc = login_for_students_uc
        self.change_password_by_student_uc = change_password_by_student_uc
        self.change_email_by_student_uc = change_email_by_student_uc
        self.jwt_service = jwt_service
    async def normal_login(self, email: str, password: str) -> str:
        try:
            print(
                "[debug][normal_login][controller] "
                f"request email={email!r} password_len={len(password or '')}"
            )
            token = await self.login_for_students_uc.normal_login(email, password)
            print("[debug][normal_login][controller] success")
            return token
        except Exception as e:
            print("[debug][normal_login][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def change_password(self, student_id: str, old_password: str, new_password: str) -> str:
        try:
            print(
                "[debug][change_password][controller] "
                f"request student_id={student_id!r} old_password_len={len(old_password or '')} new_password_len={len(new_password or '')}"
            )
            result = await self.change_password_by_student_uc.change_password_by_student(student_id, old_password, new_password)
            print("[debug][change_password][controller] success")
            return result
        except Exception as e:
            print("[debug][change_password][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def change_email(self, student_id: str, current_password: str, new_email: str):
        try:
            print(
                "[debug][change_email][controller] "
                f"request student_id={student_id!r} current_password_len={len(current_password or '')} new_email={new_email!r}"
            )
            
            # 1. Request email change (saves token to DB & dispatches EmailChangedEvent)
            await self.change_email_by_student_uc.change_email_by_user(
                student_id=student_id,
                new_email=new_email,
                current_password=current_password
            )
            
            print("[debug][change_email][controller] success")
            
            # 2. Return response (Do NOT call verify_email here!)
            return {
                "message": "Email change requested. Please check your new inbox to verify the update."
            }
            
        except Exception as e:
            print("[debug][change_email][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))