from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException

class GetStudentInfoByRegistrationNumberUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_student_info_by_registration_number(self, registration_number: str) -> dict:
        student_info = await self.user_repo.get_student_info_by_registration_number(registration_number)
        if student_info is None:
            raise DataFetchFailedException("Failed to fetch student info.")
        return student_info