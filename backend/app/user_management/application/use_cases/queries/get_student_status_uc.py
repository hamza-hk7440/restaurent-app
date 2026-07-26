from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import UserNotFoundException
from user_management.domain.value_objects.status import StudentStatus

class GetStudentStatusUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_student_status(self, student_id: str) -> StudentStatus:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        return student.status