from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import InvalidTokenException
from user_management.application.services.jwt_service import IJWTService

class LogoutUseCase:
    def __init__(self, user_repo: IUserRepository, jwt_service: IJWTService):
        self.user_repo = user_repo
        self.jwt_service = jwt_service

    async def execute(self, token: str) -> None:
        student_id = await self.jwt_service.verify_refresh_token(token)
        if not student_id:
            raise InvalidTokenException("Invalid token.")

        await self.jwt_service.delete_token(token)