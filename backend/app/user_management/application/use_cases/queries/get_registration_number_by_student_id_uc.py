from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException

class GetRegistrationNumberByStudentIdUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_registration_number_by_student_id(self, student_id: str) -> str:
        registration_number = await self.user_repo.get_registration_number_by_student_id(student_id)
        if registration_number is None:
            raise DataFetchFailedException("Failed to fetch registration number.")
        return registration_number