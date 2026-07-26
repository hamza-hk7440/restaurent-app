from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.services.password_service import IPasswordService
from user_management.domain.events.user_events import PasswordChangedEvent
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.exceptions.exception import UserUpdateFailedException,UserNotFoundException
from user_management.application.services.password_generator_service import IPasswordGeneratorService
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService

class ChangePasswordByAdminUseCase:
    def __init__(self, user_repo: IUserRepository, password_service: IPasswordService, events_repo: IEventRepository, password_generator_service: IPasswordGeneratorService, send_mail_service: ISendMailForWlcAndPasswordService):
        self.user_repo = user_repo
        self.password_service = password_service
        self.events_repo = events_repo
        self.password_generator_service = password_generator_service
        self.send_mail_service = send_mail_service

    async def change_password_by_admin(self, student_id: str) -> None:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        
        new_password = self.password_generator_service.generate_password()
        hashed_new_password = self.password_service.hash_password(new_password)
        
        updated_student = await self.user_repo.change_password(student_id, hashed_new_password)
        if not updated_student:
            raise UserUpdateFailedException("Failed to update password.")
        
        event = PasswordChangedEvent(user_id=student.student_id)
        await self.events_repo.dispatch(event)
        await self.send_mail_service.send_password_reset_email(student.email, new_password)