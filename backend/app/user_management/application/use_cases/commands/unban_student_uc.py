from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.events.user_events import  UnbannedStudentEvent
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.exceptions.exception import UserNotFoundException,BanStudentFailedException

class UnbanStudentUseCase:
    def __init__(self, user_repo: IUserRepository, events_repo: IEventRepository):
        self.user_repo = user_repo
        self.events_repo = events_repo

    async def unban_student(self, student_id: str) -> None:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        
        updated_student = await self.user_repo.unban_student(student_id)
        if not updated_student:
            raise BanStudentFailedException("Failed to unban student.")
        
        event = UnbannedStudentEvent(user_id=student.student_id)
        await self.events_repo.dispatch(event)