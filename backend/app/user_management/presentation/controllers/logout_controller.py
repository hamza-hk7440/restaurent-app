from fastapi import HTTPException
import traceback
from user_management.application.services.jwt_service import IJWTService
from user_management.application.use_cases.commands.logout_uc import LogoutUseCase
from user_management.domain.interfaces.user_repo import IUserRepository
class LogoutController:
    def __init__(self, student_repo: IUserRepository, jwt_service: IJWTService):
        self.student_repo = student_repo
        self.jwt_service = jwt_service
        self.logout_uc = LogoutUseCase(user_repo=student_repo, jwt_service=jwt_service)

    async def logout(self, token: str) -> str:
        try:
            print(
                "[debug][logout][controller] "
                f"request token_len={len(token or '')}"
            )
            await self.logout_uc.execute(token)
            print("[debug][logout][controller] success")
            return "Logout successful."
        except Exception as e:
            print("[debug][logout][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))