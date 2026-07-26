from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.services.password_service import IPasswordService
from user_management.domain.events.user_events import EmailChangedEvent
from user_management.application.exceptions.exception import UserUpdateFailedException,UserNotFoundException,InvalidCredentialsException
from user_management.domain.interfaces.events_repo import IEventRepository
class ChangeEmailByStudentUseCase:
    def __init__(self, user_repo: IUserRepository, password_service: IPasswordService, events_repo: IEventRepository):
        self.user_repo = user_repo
        self.password_service = password_service
        self.events_repo = events_repo

    async def change_email_by_user(self, student_id: str, new_email: str, current_password: str) -> None:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        if not self.password_service.verify_password(current_password, student.password):
            raise InvalidCredentialsException("Current password is incorrect.")
        updated_student = await self.user_repo.edit_email(student_id, new_email)
        if not updated_student:
            raise UserUpdateFailedException("Failed to update email.")
        event = EmailChangedEvent(user_id=student.student_id, new_email=new_email)
        await self.events_repo.dispatch(event)