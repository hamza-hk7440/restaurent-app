from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.services.jwt_service import IJWTService
from user_management.application.exceptions.exception import InvalidCredentialsException
from user_management.application.services.password_service import IPasswordService
class LoginForAdminUseCase:
    def __init__(
        self, 
        admin_repo: IUserRepository, 
        jwt_service: IJWTService,
        password_service: IPasswordService
    ):
        self.admin_repo = admin_repo
        self.jwt_service = jwt_service
        self.password_service = password_service

    async def execute(self, email: str, password: str) -> str:
        admin = await self.admin_repo.get_admin_by_email(email)
        if not admin or not self.password_service.verify_password(password, admin.password):
            raise InvalidCredentialsException("Invalid email or password.")

        token = self.jwt_service.generate_token(user_id=str(admin.admin_id), expires_delta=None)
        return token