from datetime import datetime, timedelta,timezone
from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.events.user_events import EmailChangedEvent
from user_management.application.exceptions.exception import UserUpdateFailedException,UserNotFoundException
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.jwt_service import IJWTService
from user_management.infrastructure.events.user_event_handler import EmailChangedEventHandler

class ChangeEmailByAdminUseCase:
    def __init__(self, user_repo: IUserRepository, events_repo: IEventRepository,
                 jwt_service: IJWTService, email_changed_event_handler: EmailChangedEventHandler):
        self.user_repo = user_repo
        self.events_repo = events_repo
        self.jwt_service = jwt_service
        self.email_changed_event_handler = email_changed_event_handler

    async def change_email_by_admin(self, student_id: str, new_email: str) -> None:
        verification_token = self.jwt_service.generate_verification_token()
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        updated_student = await self.user_repo.edit_email(
            student_id=student_id,
            email=new_email,
            verification_token=verification_token
        )
        if not updated_student:
            raise UserUpdateFailedException("Failed to update email.")
        event = EmailChangedEvent(user_id=student.student_id, new_email=new_email,changed_at=datetime.now(timezone.utc), verification_token=verification_token)
        await self.email_changed_event_handler.handle(event)