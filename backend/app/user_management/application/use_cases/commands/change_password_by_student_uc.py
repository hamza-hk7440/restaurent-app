from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.services.password_service import IPasswordService
from user_management.domain.events.user_events import PasswordChangedEvent
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.exceptions.exception import UserUpdateFailedException,UserNotFoundException,InvalidCredentialsException


class ChangePasswordByStudentUseCase:
    def __init__(self, user_repo: IUserRepository, password_service: IPasswordService, events_repo: IEventRepository):
        self.user_repo = user_repo
        self.password_service = password_service
        self.events_repo = events_repo

    async def change_password_by_student(self, student_id: str, current_password: str, new_password: str) -> None:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        if not self.password_service.verify_password(current_password, student.password):
            raise InvalidCredentialsException("Current password is incorrect.")
        hashed_new_password = self.password_service.hash_password(new_password)
        updated_student = await self.user_repo.change_password(student_id, hashed_new_password)
        if not updated_student:
            raise UserUpdateFailedException("Failed to update password.")
        event = PasswordChangedEvent(user_id=student.student_id)
        await self.events_repo.dispatch(event)