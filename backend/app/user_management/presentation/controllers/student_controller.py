from fastapi import HTTPException
import traceback
from user_management.application.use_cases.commands.login_for_students_uc import LoginForStudentsUseCase
class StudentController:
    def __init__(self, login_for_students_uc: LoginForStudentsUseCase):
        self.login_for_students_uc = login_for_students_uc
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
