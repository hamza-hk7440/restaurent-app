from user_management.application.services.forget_password_service import IForgetPasswordService
from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.infrastructure.external.jwt_repository import JWTRepository
from user_management.infrastructure.external.send_mail_repository import SendMailForWlcAndPasswordService
class ForgetPasswordRepository(IForgetPasswordService):
    def __init__(self, user_repository: IUserRepository,
                 jwt_repository: JWTRepository,
                 send_mail_service: SendMailForWlcAndPasswordService):
        self.user_repository = user_repository
        self.jwt_repository = jwt_repository
        self.send_mail_service = send_mail_service
    async def request_reset(self, email: str) -> None:
        try:
            student = await self.user_repository.get_student_by_email(email)
            if not student:
                raise ValueError("Student not found")
            reset_token = self.jwt_repository.generate_password_reset_token()
            expiry_time=self.jwt_repository.get_token_expiry_time()
            await self.jwt_repository.save_token(reset_token, expiry_time)
            reset_link = f"{self.send_mail_service.settings.FRONTEND_URL}/reset-password?token={reset_token}"
            await self.send_mail_service.send_password_reset_email(email, reset_link)
        except Exception as e:
            raise e
    async def reset_password(self, token: str, new_password: str) -> None:
        try:
            student_id = await self.jwt_repository.verify_password_reset_token(token)
            if not student_id:
                raise ValueError("Invalid or expired token")
            await self.user_repository.change_password(student_id, new_password)
            await self.jwt_repository.delete_token(token)
        except Exception as e:
            raise e