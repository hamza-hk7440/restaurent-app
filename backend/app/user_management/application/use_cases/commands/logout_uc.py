from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import UserNotFoundException
from user_management.application.services.jwt_service import IJWTService

class LogoutUseCase:
    def __init__(self, user_repo: IUserRepository, jwt_service: IJWTService):
        self.user_repo = user_repo
        self.jwt_service = jwt_service

    async def execute(self, token: str) -> None:
        student_id = self.jwt_service.verify_token(token)
        if not student_id:
            raise UserNotFoundException("User not found.")

        await self.user_repo.logout_user(student_id)