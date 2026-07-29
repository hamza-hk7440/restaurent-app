from user_management.application.exceptions.exception import (
    UserNotFoundException,
    UnbanStudentFailedException,
)
from user_management.domain.events.student_events import UnbannedStudentEvent

class UnbanStudentUseCase:
    def __init__(self, user_repo: IUserRepository, events_repo: IEventRepository):
        self.user_repo = user_repo
        self.events_repo = events_repo

    async def execute(self, admin_id: str, student_id: str) -> None:
        # 1. Ensure student exists
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")

        # 2. Perform the unban operation in the repository
        updated_student = await self.user_repo.unban_student(
            student_id=student_id, 
            admin_id=admin_id
        )
        if not updated_student:
            raise UnbanStudentFailedException("Failed to unban student.")

        # 3. Dispatch the domain event
        event = UnbannedStudentEvent(
            user_id=student.student_id, 
            admin_id=admin_id
        )
        await self.events_repo.dispatch(event)