from datetime import datetime, timezone
from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.services.verify_email_service import IVerifyEmailService
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService
from user_management.application.services.password_service import IPasswordService
from user_management.application.services.password_generator_service import IPasswordGeneratorService
from user_management.domain.value_objects.status import StudentStatus
from user_management.application.services.jwt_service import IJWTService
class VerifyEmailRepository(IVerifyEmailService):
    def __init__(
        self, 
        user_repo: IUserRepository, 
        send_mail_service: ISendMailForWlcAndPasswordService,
        password_service: IPasswordService,
        password_generator_service: IPasswordGeneratorService,
        jwt_service: IJWTService
    ):
        self.user_repo = user_repo
        self.send_mail_service = send_mail_service
        self.password_service = password_service
        self.password_generator_service = password_generator_service
        self.jwt_service = jwt_service

    async def verify_email(self, token: str) -> bool:
        student_id = await self.jwt_service.verify_verification_token(token)
        if not student_id:
            return False
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            return False
        password = self.password_generator_service.generate_password()
        hashed_password = self.password_service.hash_password(password)
        await self.user_repo.change_password(student.student_id, hashed_password)
        await self.user_repo.edit_student_infos(student.student_id, status=StudentStatus.ACTIVE)
        await self.send_mail_service.send_welcome_email(student.email, password)

        # Only mark the account verified after all downstream work succeeds.
        await self.user_repo.mark_email_as_verified(student.student_id)
        await self.jwt_service.delete_token(token)
        return True
    async def verify_email_for_change(self, token: str) -> bool:
        student_id = await self.jwt_service.verify_verification_token(token)
        if not student_id:
            return False
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            return False
        await self.user_repo.mark_email_as_verified(student.student_id)
        await self.jwt_service.delete_token(token)
        return True
