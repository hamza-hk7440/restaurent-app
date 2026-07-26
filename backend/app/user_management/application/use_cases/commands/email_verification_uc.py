from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.services.jwt_service import IJWTService
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService
from user_management.application.services.verify_email_service import IVerifyEmailService
from user_management.application.exceptions.exception import InvalidVerificationTokenException,UserNotFoundException
from datetime import datetime
class EmailVerificationUseCase:
    def __init__(
        self, 
        user_repo: IUserRepository, 
        jwt_service: IJWTService,
        send_mail_service: ISendMailForWlcAndPasswordService,
        verify_email_service: IVerifyEmailService
    ):
        self.user_repo = user_repo
        self.jwt_service = jwt_service
        self.send_mail_service = send_mail_service
        self.verify_email_service = verify_email_service

    async def send_verification_email(self, email: str) -> None:
        user = await self.user_repo.get_student_by_email(email)
        if not user:
            raise UserNotFoundException("User with the provided email does not exist.")
        
        verification_token = self.jwt_service.generate_verification_token(email, expires_delta=None)
        await self.jwt_service.save_token(verification_token, expires_at=None)  # Save the token with an expiration time
        verify_link=f"https://your-app.com/verify-email?token={verification_token}"
        await self.send_mail_service.send_verification_email(email, verify_link)
        return {"message": "Verification email sent successfully."}
    async def verify_email(self, token: str) -> None:
        student_id = self.jwt_service.verify_verification_token(token)
        if not student_id:
            raise InvalidVerificationTokenException("Invalid or expired verification token.")
        
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("User with the provided ID does not exist.")
        student.email_verified = True
        student.email_verified_at = datetime.utcnow()
        await self.user_repo.edit_student_infos(
            student_id=student.student_id,
            email_verified=student.email_verified,
            email_verified_at=student.email_verified_at
        )
        return {"message": "Email verified successfully."}