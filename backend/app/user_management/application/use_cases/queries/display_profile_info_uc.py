from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException
from user_management.application.dtos.student_dto import StudentDTO
class DisplayProfileInfoUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
    async def display_profile_info(self, student_id: str) -> StudentDTO:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise DataFetchFailedException("Failed to fetch student data.")
        return StudentDTO.from_entity(student)
