from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.events.user_events import PasswordChangedEvent
from user_management.application.services.forget_password_service import IForgetPasswordService
from user_management.application.services.jwt_service import IJWTService
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService
from user_management.application.exceptions.exception import UserNotFoundException,InvalidTokenException
from user_management.application.services.password_service import IPasswordService
class ForgetPasswordUseCase:
    def __init__(
        self, 
        user_repo: IUserRepository, 
        forget_password_service: IForgetPasswordService,
        jwt_service: IJWTService,
        send_mail_service: ISendMailForWlcAndPasswordService,
        password_service: IPasswordService,
        event_repo: IEventRepository
    ):
        self.user_repo = user_repo
        self.forget_password_service = forget_password_service
        self.jwt_service = jwt_service
        self.send_mail_service = send_mail_service
        self.password_service = password_service
        self.event_repo = event_repo

    async def request_reset(self, email: str) -> None:
        user = await self.user_repo.get_student_by_email(email)
        if not user:
            raise UserNotFoundException("User with the provided email does not exist.")        
        reset_token = self.jwt_service.generate_password_reset_token(email)
        await self.jwt_service.save_token(reset_token, expires_at=None) 
        reset_link=f"https://your-app.com/reset-password?token={reset_token}"
        await self.send_mail_service.send_password_reset_email(email, reset_link)
        return {"message": "Password reset email sent successfully."}
    async def reset_password(self, token: str, new_password: str) -> None:
        student_id=self.jwt_service.verify_password_reset_token(token)
        if not student_id:
            raise InvalidTokenException("Invalid or expired token.")
        hashed=self.password_service.hash_password(new_password)
        student=await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("User with the provided email does not exist.")
        await self.user_repo.change_password(student_id,hashed)
        event=PasswordChangedEvent(student_id=student_id)
        await self.event_repo.dispatch(event)
        return {"message": "Password reset successfully."}
        